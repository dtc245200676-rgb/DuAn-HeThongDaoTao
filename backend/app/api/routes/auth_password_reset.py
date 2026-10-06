import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.security import (
    RESET_TOKEN_EXPIRE_MINUTES,
    generate_one_time_token,
    hash_one_time_token,
    hash_password,
    utcnow,
    validate_password,
)
from app.db.database import get_db
from app.models.session import AuthSession
from app.models.tokens import PasswordResetToken
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    MessageResponse,
    ResetPasswordRequest,
)
from app.services.email_service import email_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

GENERIC_RESET_MESSAGE = "Nếu email tồn tại trong hệ thống, hướng dẫn đặt lại mật khẩu đã được gửi."


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if user:
        now = utcnow()
        db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )

        raw_token = generate_one_time_token()
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_one_time_token(raw_token),
                expires_at=now + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
            )
        )
        db.commit()

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        reset_url = f"{frontend_url}/reset-password?token={raw_token}"
        email_service.send(
            user.email,
            "Đặt lại mật khẩu - Hệ thống đào tạo CodeGym",
            f"Liên kết đặt lại mật khẩu có hiệu lực {RESET_TOKEN_EXPIRE_MINUTES} phút và chỉ dùng một lần:\n{reset_url}",
        )

    return ForgotPasswordResponse(message=GENERIC_RESET_MESSAGE)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        validate_password(data.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    token = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_one_time_token(data.token),
            PasswordResetToken.used_at.is_(None),
        )
    )
    now = utcnow()

    if not token or token.expires_at <= now:
        raise HTTPException(
            status_code=400,
            detail="Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.",
        )

    user = db.get(User, token.user_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Liên kết đặt lại mật khẩu không hợp lệ.",
        )

    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    user.failed_login_attempts = 0
    user.locked_until = None
    token.used_at = now

    db.execute(
        update(AuthSession)
        .where(
            AuthSession.user_id == user.id,
            AuthSession.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )
    db.commit()

    return MessageResponse(
        message="Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại."
    )
