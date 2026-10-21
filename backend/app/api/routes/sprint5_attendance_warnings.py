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

@router.get("/attendance/warnings")
def attendance_warnings(threshold: float = Query(20, ge=1, le=100), context: AuthContext = Depends(require_permission("attendance.view")), db: Session = Depends(get_db)):
    _require_staff(context)
    classes = db.scalars(select(TrainingClass).order_by(TrainingClass.id.desc())).all()
    results = []
    for cl in classes:
        try:
            _can_manage_class(db, cl.id, context)
        except HTTPException:
            continue
        _, students = _attendance_metrics(db, cl.id, threshold)
        for student in students:
            if student["warning"]:
                results.append({**student, "class_id": cl.id, "class_code": cl.code or cl.name, "threshold": threshold})
    results.sort(key=lambda x: (-x["absence_rate"], x["class_code"], x["student_code"] or ""))
    return {"threshold": threshold, "total": len(results), "items": results}


@router.post("/attendance/warnings/notify")
def notify_attendance_warnings(threshold: float = Query(20, ge=1, le=100), context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    _require_staff(context)
    classes = db.scalars(select(TrainingClass).order_by(TrainingClass.id.desc())).all()
    warnings = []
    for cl in classes:
        try:
            _can_manage_class(db, cl.id, context)
        except HTTPException:
            continue
        _, students = _attendance_metrics(db, cl.id, threshold)
        warnings.extend([{**s, "class_id": cl.id, "class_code": cl.code or cl.name} for s in students if s["warning"]])
    if not warnings:
        return {"message": "Hiện chưa có học viên vượt ngưỡng cảnh báo.", "notified": 0}
    manager_users = db.scalars(select(User).options(selectinload(User.roles))).all()
    recipients = {u.id for u in manager_users if set(r.slug for r in u.roles) & MANAGER_ROLES}
    for cl in classes:
        try:
            _can_manage_class(db, cl.id, context)
        except HTTPException:
            continue
        cs_ids = select(ClassSubject.id).where(ClassSubject.class_id == cl.id)
        recipients.update(db.scalars(select(ClassSubjectStaff.user_id).where(ClassSubjectStaff.class_subject_id.in_(cs_ids), ClassSubjectStaff.staff_role == "teacher")).all())
    existing = db.scalars(select(UserNotification).where(UserNotification.title == "S5 · Cảnh báo chuyên cần", UserNotification.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))).all()
    already = {(n.user_id, n.message) for n in existing}
    notified = 0
    for warning in warnings:
        message_text = f"{warning['class_code']}: {warning['full_name']} vắng {warning['absence_rate']}%, vượt ngưỡng {threshold}% (mã {warning['student_code']})."
        for user_id in recipients:
            if (user_id, message_text) not in already:
                notify(db, user_id, "S5 · Cảnh báo chuyên cần", message_text, "/s5/attendance")
                already.add((user_id, message_text)); notified += 1
    db.commit()
    return {"message": "Đã gửi cảnh báo chuyên cần.", "notified": notified, "students": len(warnings)}
