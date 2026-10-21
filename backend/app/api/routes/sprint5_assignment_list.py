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

@router.get("/assignments")
def list_assignments(class_id: int | None = None, context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    _require_staff(context)
    stmt = select(Assignment).order_by(Assignment.created_at.desc())
    if class_id is not None:
        _can_manage_class(db, class_id, context)
        stmt = stmt.join(AssignmentClass, AssignmentClass.assignment_id == Assignment.id).where(AssignmentClass.class_id == class_id)
    rows = db.scalars(stmt).unique().all()
    out = []
    for row in rows:
        class_ids = _assignment_class_ids(db, row.id)
        if "teacher" in context.role_slugs and not (set(context.role_slugs) & MANAGER_ROLES):
            if not class_ids or any(_teacher_can_class(db, cid, context) for cid in class_ids):
                out.append(_serialize_assignment(db, row))
        else:
            out.append(_serialize_assignment(db, row))
    return out


@router.get("/assignments/mine")
def my_assignments(context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    student = _student_profile(db, context)
    enrollments = db.scalars(select(ClassEnrollment).where(ClassEnrollment.student_id == student.id, ClassEnrollment.status == "active")).all()
    class_ids = [e.class_id for e in enrollments]
    if not class_ids: return []
    ids = select(AssignmentClass.assignment_id).where(AssignmentClass.class_id.in_(class_ids))
    rows = db.scalars(select(Assignment).where(Assignment.id.in_(ids), Assignment.status == "published").order_by(Assignment.due_at)).all()
    return [_serialize_assignment(db, item, student.id) for item in rows]


@router.patch("/assignments/{assignment_id}")
def update_assignment(assignment_id: int, data: dict, context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    _require_staff(context)
    item = db.get(Assignment, assignment_id)
    if not item: raise HTTPException(404, "Không tìm thấy bài tập.")
    class_ids = _assignment_class_ids(db, item.id)
    for class_id in class_ids: _can_manage_class(db, class_id, context)
    allowed = {"due_at", "allow_late", "status"}
    unknown = set(data) - allowed
    if unknown: raise HTTPException(422, f"Trường không được cập nhật: {', '.join(sorted(unknown))}")
    if "due_at" in data:
        try: item.due_at = datetime.fromisoformat(data["due_at"].replace("Z", "+00:00")).replace(tzinfo=None)
        except (ValueError, AttributeError): raise HTTPException(422, "Hạn nộp không hợp lệ.")
    if "allow_late" in data: item.allow_late = bool(data["allow_late"])
    if "status" in data:
        if data["status"] not in {"draft", "published", "archived"}: raise HTTPException(422, "Trạng thái bài tập không hợp lệ.")
        item.status = data["status"]
    db.commit(); db.refresh(item)
    return _serialize_assignment(db, item)
