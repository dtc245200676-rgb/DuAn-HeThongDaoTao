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

@router.get("/classes")
def class_options(context: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingClass).order_by(TrainingClass.id.desc())).all()
    if "teacher" in context.role_slugs and not (set(context.role_slugs) & MANAGER_ROLES):
        allowed_ids = set(db.scalars(select(ClassSubject.class_id).join(ClassSubjectStaff, ClassSubjectStaff.class_subject_id == ClassSubject.id).where(ClassSubjectStaff.user_id == context.user.id, ClassSubjectStaff.staff_role == "teacher")).all())
        rows = [r for r in rows if r.id in allowed_ids]
    return [{"id": r.id, "code": r.code or r.name, "name": r.name, "status": r.status} for r in rows]


@router.get("/attendance/classes/{class_id}/matrix")
def attendance_matrix(class_id: int, threshold: float = Query(20, ge=1, le=100), context: AuthContext = Depends(require_permission("attendance.view")), db: Session = Depends(get_db)):
    _can_manage_class(db, class_id, context)
    cl = db.get(TrainingClass, class_id)
    if not cl:
        raise HTTPException(404, "Không tìm thấy lớp.")
    sessions, students = _attendance_metrics(db, class_id, threshold)
    return {"class_id": class_id, "class_code": cl.code or cl.name, "threshold": threshold,
            "sessions": [{"id": s.id, "start_at": s.start_at.isoformat(), "status": s.status} for s in sessions],
            "students": students}
