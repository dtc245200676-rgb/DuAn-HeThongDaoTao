import json
import re
from datetime import datetime, date
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, get_current_context, require_permission
from app.api.routes.sprint4_common import notify
from app.db.database import get_db
from app.models.sprint3 import ClassEnrollment, ClassSubject, ClassSubjectStaff, StudentProfile
from app.models.sprint4 import AttendanceRecord, ClassScheduleSession, UserNotification
from app.models.sprint5 import Assignment, AssignmentClass, AssignmentExtension, AssignmentSubmission
from app.models.training import TrainingClass
from app.models.user import User

from app.api.routes.sprint5_common import (_require_staff, _can_manage_class, _student_profile, _class_label, _attendance_metrics, _assignment_class_ids, _student_due_at, _latest_submission, _serialize_submission, _serialize_assignment, _teacher_can_class, UPLOAD_DIR, MAX_FILE_BYTES, ALLOWED_EXTENSIONS, STAFF_ROLES, MANAGER_ROLES)

router = APIRouter(prefix="/api/s5", tags=["Sprint 5 · Chuyên cần và bài tập"])

@router.post("/assignments/{assignment_id}/extensions")
def grant_extension(assignment_id: int, data: dict, context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    _require_staff(context)
    item = db.get(Assignment, assignment_id)
    if not item: raise HTTPException(404, "Không tìm thấy bài tập.")
    for class_id in _assignment_class_ids(db, item.id): _can_manage_class(db, class_id, context)
    try:
        student_id = int(data["student_id"])
        extended_due_at = datetime.fromisoformat(str(data["extended_due_at"]).replace("Z", "+00:00")).replace(tzinfo=None)
        reason = str(data["reason"]).strip()
    except (KeyError, ValueError, TypeError): raise HTTPException(422, "Thông tin gia hạn không hợp lệ.")
    if not reason: raise HTTPException(422, "Vui lòng nhập lý do gia hạn.")
    student = db.get(StudentProfile, student_id)
    if not student: raise HTTPException(404, "Không tìm thấy học viên.")
    class_ids = _assignment_class_ids(db, item.id)
    if not db.scalar(select(ClassEnrollment.id).where(ClassEnrollment.student_id == student_id, ClassEnrollment.class_id.in_(class_ids), ClassEnrollment.status == "active")):
        raise HTTPException(422, "Học viên không thuộc lớp được giao bài tập.")
    ext = db.scalar(select(AssignmentExtension).where(AssignmentExtension.assignment_id == item.id, AssignmentExtension.student_id == student_id))
    if ext:
        ext.extended_due_at = extended_due_at; ext.reason = reason; ext.granted_by_user_id = context.user.id
    else:
        db.add(AssignmentExtension(assignment_id=item.id, student_id=student_id, extended_due_at=extended_due_at, reason=reason, granted_by_user_id=context.user.id))
    db.commit()
    notify(db, student.user_id, "Gia hạn bài tập", f"Bài tập '{item.title}' đã được gia hạn đến {extended_due_at:%d/%m/%Y %H:%M}.", "/s5/assignments")
    db.commit()
    return {"message": "Đã gia hạn bài tập.", "student_id": student_id, "extended_due_at": extended_due_at.isoformat()}


@router.get("/assignments/{assignment_id}/submissions")
def list_submissions(assignment_id: int, class_id: int | None = None, context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    _require_staff(context)
    item = db.get(Assignment, assignment_id)
    if not item: raise HTTPException(404, "Không tìm thấy bài tập.")
    class_ids = _assignment_class_ids(db, item.id)
    for cid in class_ids: _can_manage_class(db, cid, context)
    stmt = select(AssignmentSubmission).where(AssignmentSubmission.assignment_id == assignment_id).order_by(AssignmentSubmission.student_id, AssignmentSubmission.version.desc())
    rows = db.scalars(stmt).all()
    if class_id is not None and class_id not in class_ids: raise HTTPException(422, "Lớp không thuộc bài tập.")
    if class_id is not None:
        student_ids = select(ClassEnrollment.student_id).where(ClassEnrollment.class_id == class_id, ClassEnrollment.status == "active")
        rows = [r for r in rows if r.student_id in set(db.scalars(student_ids).all())]
    return [_serialize_submission(db, row) for row in rows]


@router.patch("/submissions/{submission_id}/grade")
def grade_submission(submission_id: int, data: dict, context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    _require_staff(context)
    item = db.get(AssignmentSubmission, submission_id)
    if not item: raise HTTPException(404, "Không tìm thấy bài nộp.")
    assignment = db.get(Assignment, item.assignment_id)
    for class_id in _assignment_class_ids(db, assignment.id): _can_manage_class(db, class_id, context)
    status = data.get("status", "graded")
    if status not in {"graded", "needs_revision"}: raise HTTPException(422, "Trạng thái chấm bài không hợp lệ.")
    score = data.get("score")
    if score is not None:
        try: score = float(score)
        except (ValueError, TypeError): raise HTTPException(422, "Điểm không hợp lệ.")
        if score < 0 or score > float(assignment.max_score): raise HTTPException(422, f"Điểm phải từ 0 đến {float(assignment.max_score)}.")
    item.score = score; item.feedback = str(data.get("feedback", ""))[:4000]; item.status = status
    item.graded_by_user_id = context.user.id; item.graded_at = datetime.now()
    db.commit()
    student = db.get(StudentProfile, item.student_id)
    if student: notify(db, student.user_id, "Bài tập đã được phản hồi", f"Bài '{assignment.title}' đã được cập nhật: {'cần làm lại' if status == 'needs_revision' else 'đã chấm điểm'}.", "/s5/assignments")
    db.commit()
    return {"message": "Đã lưu kết quả chấm bài.", "submission": _serialize_submission(db, item)}


@router.get("/assignments/progress/{class_id}")
def assignment_progress(class_id: int, status: str | None = None, context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    _require_staff(context); _can_manage_class(db, class_id, context)
    assignment_ids = select(AssignmentClass.assignment_id).where(AssignmentClass.class_id == class_id)
    assignments = db.scalars(select(Assignment).where(Assignment.id.in_(assignment_ids)).order_by(Assignment.due_at)).all()
    enrollments = db.scalars(select(ClassEnrollment).where(ClassEnrollment.class_id == class_id, ClassEnrollment.status == "active")).all()
    students = []
    for enrollment in enrollments:
        sp = db.get(StudentProfile, enrollment.student_id); user = db.get(User, sp.user_id) if sp else None
        if sp and user: students.append((sp, user))
    results = []
    for assignment in assignments:
        rows = []
        for sp, user in students:
            latest = _latest_submission(db, assignment.id, sp.id)
            due = _student_due_at(db, assignment.id, sp.id, assignment.due_at)
            state = latest.status if latest else ("overdue" if datetime.now() > due else "not_submitted")
            if latest and latest.is_late and latest.status not in {"graded", "needs_revision"}: state = "late"
            if status and state != status: continue
            rows.append({"student_id": sp.id, "student_code": sp.student_code, "student_name": user.full_name,
                         "status": state, "submitted_at": latest.submitted_at.isoformat() if latest else None,
                         "is_late": bool(latest.is_late) if latest else False, "score": float(latest.score) if latest and latest.score is not None else None,
                         "submission_id": latest.id if latest else None, "feedback": latest.feedback if latest else None})
        results.append({**_serialize_assignment(db, assignment), "students": rows,
                        "total_students": len(students), "submitted_count": sum(bool(r["submitted_at"]) for r in rows),
                        "graded_count": sum(r["status"] == "graded" for r in rows),
                        "late_count": sum(r["is_late"] for r in rows)})
    return {"class_id": class_id, "items": results}
