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

@router.post("/assignments")
async def create_assignment(
    title: str = Form(...), description: str = Form(""), class_ids: str = Form(...),
    due_at: datetime = Form(...), max_score: float = Form(10), allow_late: bool = Form(False),
    publish: bool = Form(True), files: list[UploadFile] = File(default=[]),
    context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db),
):
    _require_staff(context)
    if not title.strip(): raise HTTPException(422, "Tiêu đề bài tập không được để trống.")
    if max_score <= 0: raise HTTPException(422, "Điểm tối đa phải lớn hơn 0.")
    try:
        ids = list(dict.fromkeys(int(x) for x in json.loads(class_ids)))
    except (ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(422, "Danh sách lớp không hợp lệ.")
    if not ids: raise HTTPException(422, "Hãy chọn ít nhất một lớp.")
    for class_id in ids:
        if not db.get(TrainingClass, class_id): raise HTTPException(404, f"Không tìm thấy lớp {class_id}.")
        _can_manage_class(db, class_id, context)
    file_items = []
    saved_paths = []
    for upload in files:
        if not upload or not upload.filename: continue
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS: raise HTTPException(422, f"Định dạng tệp {suffix or '(không có phần mở rộng)'} không được hỗ trợ.")
        content = await upload.read()
        if len(content) > MAX_FILE_BYTES: raise HTTPException(413, f"Tệp {upload.filename} vượt quá 20 MB.")
        stored = f"{uuid4().hex}{suffix}"
        target = UPLOAD_DIR / stored; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(content); saved_paths.append(target)
        file_items.append({"name": Path(upload.filename).name, "path": f"assignments/{stored}", "size": len(content)})
    item = Assignment(title=title.strip(), description=description.strip() or None, due_at=due_at,
                      max_score=max_score, allow_late=allow_late, status="published" if publish else "draft",
                      attachment_files=json.dumps(file_items, ensure_ascii=False), created_by_user_id=context.user.id)
    db.add(item); db.flush()
    for class_id in ids: db.add(AssignmentClass(assignment_id=item.id, class_id=class_id))
    if publish:
        enrollment_rows = db.scalars(select(ClassEnrollment).where(ClassEnrollment.class_id.in_(ids), ClassEnrollment.status == "active")).all()
        for enrollment in enrollment_rows:
            sp = db.get(StudentProfile, enrollment.student_id)
            if sp: notify(db, sp.user_id, "Bài tập mới", f"Bạn có bài tập mới: {item.title}", "/s5/assignments")
    db.commit(); db.refresh(item)
    return _serialize_assignment(db, item)
