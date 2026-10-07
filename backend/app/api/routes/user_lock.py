from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select,update
from sqlalchemy.orm import Session,selectinload
from app.api.deps import AuthContext,require_permission
from app.api.routes.users_common import serialize_user
from app.core.security import utcnow
from app.db.database import get_db
from app.models.audit import AccountLockAudit
from app.models.session import AuthSession
from app.models.user import User
from app.schemas.user import LockAccountRequest,UnlockAccountRequest
router=APIRouter(prefix="/api/users",tags=["User Lock"])
@router.post("/{user_id}/lock")
def lock_user(user_id:int,data:LockAccountRequest,context:AuthContext=Depends(require_permission("users.lock")),db:Session=Depends(get_db)):
    if user_id==context.user.id: raise HTTPException(status_code=400,detail="Không thể tự khóa tài khoản đang đăng nhập.")
    user=db.scalar(select(User).where(User.id==user_id).options(selectinload(User.roles)))
    if not user: raise HTTPException(status_code=404,detail="Không tìm thấy người dùng.")
    now=utcnow();user.is_active=False;user.status="locked";user.needs_handover=True;db.execute(update(AuthSession).where(AuthSession.user_id==user.id,AuthSession.revoked_at.is_(None)).values(revoked_at=now));db.add(AccountLockAudit(user_id=user.id,actor_user_id=context.user.id,action="lock",reason=data.reason.strip()));db.commit();return {"message":"Đã khóa tài khoản và thu hồi toàn bộ phiên đăng nhập.","handover_warning":"Cần kiểm tra và bàn giao các lớp/công việc mà người dùng này đang phụ trách.","user":serialize_user(user)}
@router.post("/{user_id}/unlock")
def unlock_user(user_id:int,data:UnlockAccountRequest,context:AuthContext=Depends(require_permission("users.lock")),db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.id==user_id).options(selectinload(User.roles)))
    if not user: raise HTTPException(status_code=404,detail="Không tìm thấy người dùng.")
    user.is_active=True;user.status="active";user.needs_handover=False;db.add(AccountLockAudit(user_id=user.id,actor_user_id=context.user.id,action="unlock",reason=data.reason.strip()));db.commit();return {"message":"Đã mở khóa tài khoản.","user":serialize_user(user)}
