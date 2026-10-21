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

@router.get("/attendance/me")
def my_attendance(context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    student = _student_profile(db, context)
    enrollments = db.scalars(select(ClassEnrollment).where(ClassEnrollment.student_id == student.id, ClassEnrollment.status == "active")).all()
    result = []
    for enrollment in enrollments:
        cl = db.get(TrainingClass, enrollment.class_id)
        sessions, students = _attendance_metrics(db, enrollment.class_id, 20)
        item = next((s for s in students if s["student_id"] == student.id), None)
        if item:
            item["class_id"] = enrollment.class_id; item["class_code"] = (cl.code or cl.name) if cl else str(enrollment.class_id)
            item["history"] = [{**h, "class_code": item["class_code"]} for h in item["history"]]
            result.append(item)
    return {"items": result, "total": len(result)}
