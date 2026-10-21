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

@router.post("/assignments/{assignment_id}/submissions")
async def submit_assignment(assignment_id: int, comment: str = Form(""), files: list[UploadFile] = File(...), context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    student = _student_profile(db, context)
    item = db.get(Assignment, assignment_id)
    if not item or item.status != "published": raise HTTPException(404, "Không tìm thấy bài tập đang mở.")
    class_ids = _assignment_class_ids(db, item.id)
    enrolled = db.scalar(select(ClassEnrollment.id).where(ClassEnrollment.student_id == student.id, ClassEnrollment.class_id.in_(class_ids), ClassEnrollment.status == "active"))
    if not enrolled: raise HTTPException(403, "Bài tập không được giao cho lớp của bạn.")
    if not files or not any(f and f.filename for f in files): raise HTTPException(422, "Hãy chọn ít nhất một tệp để nộp.")
    due_at = _student_due_at(db, item.id, student.id, item.due_at)
    is_late = datetime.now() > due_at
    if is_late and not item.allow_late:
        raise HTTPException(422, f"Đã quá hạn nộp ({due_at:%d/%m/%Y %H:%M}) và bài tập không cho phép nộp muộn.")
    content_items = []
    buffered = []
    for upload in files:
        if not upload or not upload.filename: continue
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS: raise HTTPException(422, f"Định dạng tệp {suffix or '(không có phần mở rộng)'} không được hỗ trợ.")
        content = await upload.read()
        if len(content) > MAX_FILE_BYTES: raise HTTPException(413, f"Tệp {upload.filename} vượt quá 20 MB.")
        stored = f"{uuid4().hex}{suffix}"
        buffered.append((UPLOAD_DIR / stored, content))
        content_items.append({"name": Path(upload.filename).name, "path": f"assignments/{stored}", "size": len(content)})
    latest = _latest_submission(db, item.id, student.id)
    version = (latest.version + 1) if latest else 1
    for path, content in buffered:
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content)
    submission = AssignmentSubmission(assignment_id=item.id, student_id=student.id, version=version,
        file_items=json.dumps(content_items, ensure_ascii=False), comment=comment.strip() or None,
        status="submitted", is_late=is_late, submitted_at=datetime.now())
    db.add(submission); db.commit(); db.refresh(submission)
    return {"message": "Đã nộp bài tập.", "submission": _serialize_submission(db, submission)}
