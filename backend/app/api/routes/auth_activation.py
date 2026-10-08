from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import hash_one_time_token,utcnow,verify_password
from app.db.database import get_db
from app.models.tokens import ActivationToken
from app.models.user import User
from app.schemas.auth import ActivateAccountRequest,MessageResponse
router=APIRouter(prefix="/api/auth",tags=["Authentication"])
@router.post("/activate",response_model=MessageResponse)
def activate_account(data:ActivateAccountRequest,db:Session=Depends(get_db)):
    token=db.scalar(select(ActivationToken).where(ActivationToken.token_hash==hash_one_time_token(data.token),ActivationToken.used_at.is_(None)));now=utcnow()
    if not token or token.expires_at<=now: raise HTTPException(status_code=400,detail="Liên kết kích hoạt không hợp lệ hoặc đã hết hạn.")
    user=db.get(User,token.user_id)
    if not user or not verify_password(data.temporary_password,user.password_hash): raise HTTPException(status_code=400,detail="Mật khẩu tạm không đúng.")
    user.is_active=True;user.status="active";user.must_change_password=True;token.used_at=now;db.commit();return MessageResponse(message="Kích hoạt tài khoản thành công. Hãy đăng nhập và đổi mật khẩu tạm.")
