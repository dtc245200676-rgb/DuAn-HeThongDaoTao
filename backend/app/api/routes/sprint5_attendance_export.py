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

@router.get("/attendance/classes/{class_id}/export")
def export_attendance(class_id: int, threshold: float = Query(20, ge=1, le=100), context: AuthContext = Depends(require_permission("attendance.view")), db: Session = Depends(get_db)):
    _can_manage_class(db, class_id, context)
    cl = db.get(TrainingClass, class_id)
    if not cl:
        raise HTTPException(404, "Không tìm thấy lớp.")
    sessions, students = _attendance_metrics(db, class_id, threshold)
    wb = Workbook(); ws = wb.active; ws.title = "Chuyen can"
    ws.append(["Mã học viên", "Họ tên"] + [s.start_at.strftime("%d/%m %H:%M") for s in sessions] + ["Có mặt", "Đi muộn", "Vắng", "Tỷ lệ chuyên cần (%)", "Cảnh báo"])
    status_labels = {"present": "Có mặt", "late": "Đi muộn", "excused_absence": "Vắng có phép", "unexcused_absence": "Vắng không phép", "not_marked": "Chưa điểm danh"}
    for student in students:
        statuses = {x["session_id"]: x["status"] for x in student["history"]}
        ws.append([student["student_code"], student["full_name"]] + [status_labels.get(statuses.get(s.id, "not_marked"), statuses.get(s.id, "not_marked")) for s in sessions] + [student["present_count"], student["late_count"], student["absence_count"], student["attendance_rate"], "Có" if student["warning"] else "Không"])
    ws.freeze_panes = "C2"; ws.auto_filter.ref = ws.dimensions
    for col in ws.columns:
        letter = col[0].column_letter
        ws.column_dimensions[letter].width = min(max(max(len(str(c.value or "")) for c in col) + 2, 12), 32)
    output = BytesIO(); wb.save(output); output.seek(0)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", cl.code or cl.name)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="attendance_{safe}.xlsx"'})
