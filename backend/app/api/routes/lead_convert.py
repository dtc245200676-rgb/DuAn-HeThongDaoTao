import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint3_common import ensure_lead_access
from app.core.security import (
    ACTIVATION_TOKEN_EXPIRE_HOURS,
    generate_one_time_token,
    generate_temporary_password,
    hash_one_time_token,
    hash_password,
    utcnow,
)
from app.db.database import get_db
from app.models.lead import Lead
from app.models.role import Role
from app.models.sprint3 import LeadStatusHistory, StudentProfile
from app.models.tokens import ActivationToken
from app.models.user import User
from app.schemas.sprint3 import ConvertLeadRequest
from app.services.email_service import email_service

router = APIRouter(prefix="/api/s3/convert", tags=["S3-03 Lead Convert"])


@router.post("/leads/{lead_id}/student")
def convert_lead_to_student(
    lead_id: int,
    data: ConvertLeadRequest,
    context: AuthContext = Depends(require_permission("leads.edit")),
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Không tìm thấy lead.")
    ensure_lead_access(lead, context)
    if lead.status != "closed":
        raise HTTPException(409, "Chỉ lead ở trạng thái Chốt mới được chuyển thành học viên.")
    if not lead.email:
        raise HTTPException(422, "Lead cần có email để tạo tài khoản học viên.")
    if db.scalar(select(StudentProfile.id).where(StudentProfile.source_lead_id == lead.id)):
        raise HTTPException(409, "Lead này đã được chuyển thành học viên.")

    email = lead.email.strip().lower()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(409, "Email của lead đã tồn tại ở một tài khoản khác.")
    student_role = db.scalar(select(Role).where(Role.slug == "student"))
    if not student_role:
        raise HTTPException(500, "Hệ thống chưa có vai trò học viên.")

    temporary_password = generate_temporary_password()
    raw_token = generate_one_time_token()
    now = utcnow()
    user = User(
        full_name=lead.full_name.strip(),
        email=email,
        phone=lead.phone,
        password_hash=hash_password(temporary_password),
        role="student",
        status="pending",
        is_active=False,
        must_change_password=True,
        roles=[student_role],
    )
    db.add(user); db.flush()
    student_code = f"HV{now.year}{user.id:05d}"
    student = StudentProfile(
        student_code=student_code,
        user_id=user.id,
        source_lead_id=lead.id,
        entry_level=data.entry_level,
        notes=data.notes,
    )
    db.add(student)
    db.add(ActivationToken(
        user_id=user.id,
        token_hash=hash_one_time_token(raw_token),
        expires_at=now + timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS),
    ))
    old_status = lead.status
    lead.status = "enrolled"
    db.add(LeadStatusHistory(
        lead_id=lead.id,
        from_status=old_status,
        to_status="enrolled",
        reason="Chuyển thành hồ sơ học viên",
        actor_user_id=context.user.id,
    ))
    db.commit(); db.refresh(student)

    frontend = os.getenv("FRONTEND_URL", "http://localhost:5173")
    activation_url = f"{frontend}/activate?token={raw_token}"
    sent = email_service.send(
        email,
        "Tài khoản học viên - Hệ thống đào tạo CodeGym",
        f"Mã học viên: {student_code}\nMật khẩu tạm: {temporary_password}\nLiên kết kích hoạt: {activation_url}",
    )
    dev = os.getenv("APP_ENV", "development") == "development"
    return {
        "message": "Đã chuyển lead thành hồ sơ học viên.",
        "student_id": student.id,
        "student_code": student_code,
        "user_id": user.id,
        "email": email,
        "email_sent": sent,
        "debug_temporary_password": temporary_password if dev else None,
        "debug_activation_token": raw_token if dev else None,
    }
