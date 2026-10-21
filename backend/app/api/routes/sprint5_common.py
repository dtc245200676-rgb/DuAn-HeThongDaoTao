import json
import re
from datetime import datetime, date
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, File, Form, HTTPException, Query, UploadFile
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


UPLOAD_DIR = Path("uploads") / "assignments"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_BYTES = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".txt", ".png", ".jpg", ".jpeg", ".csv", ".py", ".html", ".css", ".js", ".ts", ".tsx"}
STAFF_ROLES = {"system_admin", "training_manager", "academic_affairs", "teacher"}
MANAGER_ROLES = {"system_admin", "training_manager", "academic_affairs"}

def _require_staff(context: AuthContext, *, teacher_ok: bool = True):
    allowed = STAFF_ROLES if teacher_ok else MANAGER_ROLES
    if not (set(context.role_slugs) & allowed):
        raise HTTPException(403, "Bạn không có quyền thực hiện thao tác này.")

def _can_manage_class(db: Session, class_id: int, context: AuthContext):
    if set(context.role_slugs) & MANAGER_ROLES:
        return
    if "teacher" not in context.role_slugs:
        raise HTTPException(403, "Bạn không có quyền quản lý lớp này.")
    class_subject_ids = select(ClassSubject.id).where(ClassSubject.class_id == class_id)
    assigned = db.scalar(select(ClassSubjectStaff.id).where(
        ClassSubjectStaff.class_subject_id.in_(class_subject_ids),
        ClassSubjectStaff.user_id == context.user.id,
        ClassSubjectStaff.staff_role == "teacher",
    ))
    if not assigned:
        raise HTTPException(403, "Bạn chưa được phân công giảng dạy lớp này.")

def _student_profile(db: Session, context: AuthContext) -> StudentProfile:
    student = db.scalar(select(StudentProfile).where(StudentProfile.user_id == context.user.id))
    if not student:
        raise HTTPException(403, "Tài khoản hiện tại chưa có hồ sơ học viên.")
    return student

def _class_label(db: Session, class_id: int):
    item = db.get(TrainingClass, class_id)
    return (item.code or item.name) if item else str(class_id)

def _attendance_metrics(db: Session, class_id: int, threshold: float = 20):
    sessions = db.scalars(select(ClassScheduleSession).where(
        ClassScheduleSession.class_id == class_id,
        ClassScheduleSession.status.in_(["scheduled", "completed"]),
    ).order_by(ClassScheduleSession.start_at)).all()
    # Only count sessions that have already started or have attendance entered.
    session_ids = {s.id for s in sessions}
    records = db.scalars(select(AttendanceRecord).where(AttendanceRecord.schedule_session_id.in_(session_ids))).all() if session_ids else []
    marked_session_ids = {r.schedule_session_id for r in records}
    now = datetime.now()
    counted_sessions = [s for s in sessions if s.start_at <= now or s.id in marked_session_ids]
    counted_ids = {s.id for s in counted_sessions}
    record_map = {(r.schedule_session_id, r.student_id): r for r in records}
    enrollments = db.scalars(select(ClassEnrollment).where(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.status == "active",
    )).all()
    students = []
    for enrollment in enrollments:
        sp = db.get(StudentProfile, enrollment.student_id)
        if not sp:
            continue
        user = db.get(User, sp.user_id)
        present = late = absent = excused = unexcused = 0
        history = []
        for session in counted_sessions:
            rec = record_map.get((session.id, sp.id))
            status = rec.status if rec else "not_marked"
            if status == "present": present += 1
            elif status == "late": late += 1
            elif status == "excused_absence": absent += 1; excused += 1
            elif status == "unexcused_absence": absent += 1; unexcused += 1
            history.append({
                "session_id": session.id,
                "start_at": session.start_at.isoformat(),
                "status": status,
                "note": rec.note if rec else None,
            })
        total = len(counted_sessions)
        absence_rate = (absent / total * 100) if total else 0.0
        attendance_rate = ((present + late) / total * 100) if total else 0.0
        consecutive_absences = 0
        for history_item in reversed(history):
            if history_item["status"] in {"excused_absence", "unexcused_absence"}:
                consecutive_absences += 1
            elif history_item["status"] != "not_marked":
                break
        students.append({
            "student_id": sp.id, "student_code": sp.student_code,
            "full_name": user.full_name if user else sp.student_code,
            "email": user.email if user else None,
            "total_sessions": total, "present_count": present, "late_count": late,
            "absence_count": absent, "excused_absence_count": excused,
            "unexcused_absence_count": unexcused,
            "attendance_rate": round(attendance_rate, 1),
            "absence_rate": round(absence_rate, 1),
            "consecutive_absences": consecutive_absences,
            "consecutive_warning": consecutive_absences >= 2,
            "warning": total > 0 and absence_rate >= threshold,
            "history": history,
        })
    return counted_sessions, students

def _assignment_class_ids(db: Session, assignment_id: int):
    return db.scalars(select(AssignmentClass.class_id).where(AssignmentClass.assignment_id == assignment_id)).all()

def _student_due_at(db: Session, assignment_id: int, student_id: int, default_due: datetime):
    extension = db.scalar(select(AssignmentExtension).where(
        AssignmentExtension.assignment_id == assignment_id,
        AssignmentExtension.student_id == student_id,
    ))
    return extension.extended_due_at if extension else default_due

def _latest_submission(db: Session, assignment_id: int, student_id: int):
    return db.scalar(select(AssignmentSubmission).where(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == student_id,
    ).order_by(AssignmentSubmission.version.desc()).limit(1))

def _serialize_submission(db: Session, item: AssignmentSubmission):
    sp = db.get(StudentProfile, item.student_id)
    user = db.get(User, sp.user_id) if sp else None
    try:
        files = json.loads(item.file_items or "[]")
    except (TypeError, json.JSONDecodeError):
        files = []
    return {
        "id": item.id, "assignment_id": item.assignment_id, "student_id": item.student_id,
        "student_code": sp.student_code if sp else None,
        "student_name": user.full_name if user else None,
        "version": item.version, "files": files, "comment": item.comment,
        "status": item.status, "is_late": bool(item.is_late),
        "score": float(item.score) if item.score is not None else None,
        "feedback": item.feedback, "submitted_at": item.submitted_at.isoformat(),
        "graded_at": item.graded_at.isoformat() if item.graded_at else None,
    }

def _serialize_assignment(db: Session, item: Assignment, student_id: int | None = None):
    targets = db.scalars(select(AssignmentClass).where(AssignmentClass.assignment_id == item.id)).all()
    classes = [{"id": t.class_id, "code": _class_label(db, t.class_id)} for t in targets]
    try:
        attachments = json.loads(item.attachment_files or "[]")
    except (TypeError, json.JSONDecodeError):
        attachments = []
    result = {
        "id": item.id, "title": item.title, "description": item.description,
        "due_at": item.due_at.isoformat(), "max_score": float(item.max_score),
        "allow_late": bool(item.allow_late), "status": item.status,
        "classes": classes, "attachments": attachments,
        "created_at": item.created_at.isoformat(),
    }
    if student_id:
        latest = _latest_submission(db, item.id, student_id)
        due = _student_due_at(db, item.id, student_id, item.due_at)
        status = latest.status if latest else ("overdue" if datetime.now() > due else "not_submitted")
        if latest and latest.is_late and latest.status not in {"graded", "needs_revision"}:
            status = "late"
        result.update({
            "student_due_at": due.isoformat(),
            "submission_status": status,
            "latest_submission": _serialize_submission(db, latest) if latest else None,
            "is_late": bool(latest.is_late) if latest else False,
        })
    return result

def _teacher_can_class(db: Session, class_id: int, context: AuthContext):
    try:
        _can_manage_class(db, class_id, context)
        return True
    except HTTPException:
        return False
