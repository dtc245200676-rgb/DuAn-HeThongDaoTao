from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,get_current_context
from app.core.security import hash_password,utcnow,validate_password,verify_password
from app.db.database import get_db
from app.models.session import AuthSession
from app.schemas.auth import ChangePasswordRequest,MessageResponse
router=APIRouter(prefix="/api/auth",tags=["Authentication"])
@router.post("/change-password",response_model=MessageResponse)
def change_password(data:ChangePasswordRequest,context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
    if not verify_password(data.current_password,context.user.password_hash): raise HTTPException(status_code=400,detail="Mật khẩu hiện tại không đúng.")
    try: validate_password(data.new_password)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    if verify_password(data.new_password,context.user.password_hash): raise HTTPException(status_code=400,detail="Mật khẩu mới phải khác mật khẩu hiện tại.")
    context.user.password_hash=hash_password(data.new_password);context.user.must_change_password=False;now=utcnow();db.execute(update(AuthSession).where(AuthSession.user_id==context.user.id,AuthSession.id!=context.session.id,AuthSession.revoked_at.is_(None)).values(revoked_at=now));db.commit();return MessageResponse(message="Đổi mật khẩu thành công. Các phiên đăng nhập khác đã bị thu hồi.")
