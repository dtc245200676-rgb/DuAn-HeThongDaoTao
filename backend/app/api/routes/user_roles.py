from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session,selectinload
from app.api.deps import AuthContext,require_permission
from app.api.routes.users_common import load_roles,serialize_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import AssignRolesRequest
router=APIRouter(prefix="/api/users",tags=["User Roles"])
@router.put("/{user_id}/roles")
def assign_roles(user_id:int,data:AssignRolesRequest,context:AuthContext=Depends(require_permission("roles.assign")),db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.id==user_id).options(selectinload(User.roles)))
    if not user: raise HTTPException(status_code=404,detail="Không tìm thấy người dùng.")
    roles=load_roles(db,data.role_slugs);current={r.slug for r in user.roles};new={r.slug for r in roles}
    if user.id==context.user.id and "system_admin" in current and "system_admin" not in new: raise HTTPException(status_code=400,detail="Bạn không thể tự thu hồi vai trò quản trị của chính mình.")
    if not roles: raise HTTPException(status_code=400,detail="Người dùng phải có ít nhất một vai trò.")
    user.roles=roles;user.role=roles[0].slug;db.commit();db.refresh(user);return serialize_user(user)
