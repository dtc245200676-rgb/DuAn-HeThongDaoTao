import os
from datetime import timedelta
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import func,or_,select
from sqlalchemy.orm import Session,selectinload
from app.api.deps import AuthContext,require_permission
from app.api.routes.users_common import load_roles,serialize_user
from app.core.security import ACTIVATION_TOKEN_EXPIRE_HOURS,generate_one_time_token,generate_temporary_password,hash_one_time_token,hash_password,utcnow
from app.db.database import get_db
from app.models.tokens import ActivationToken
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreateRequest,UserUpdateRequest
from app.services.email_service import email_service
router=APIRouter(prefix="/api/users",tags=["User Management"])
@router.get("")
def list_users(q:str="",role:str|None=None,status:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),_:AuthContext=Depends(require_permission("users.view")),db:Session=Depends(get_db)):
    stmt=select(User).options(selectinload(User.roles));count_stmt=select(func.count(func.distinct(User.id)))
    if q.strip():
        pattern=f"%{q.strip()}%";condition=or_(User.full_name.like(pattern),User.email.like(pattern),User.phone.like(pattern));stmt=stmt.where(condition);count_stmt=count_stmt.where(condition)
    if status: stmt=stmt.where(User.status==status);count_stmt=count_stmt.where(User.status==status)
    if role: stmt=stmt.join(User.roles).where(Role.slug==role);count_stmt=count_stmt.join(User.roles).where(Role.slug==role)
    total=db.scalar(count_stmt) or 0;users=db.scalars(stmt.order_by(User.id.desc()).offset((page-1)*page_size).limit(page_size)).unique().all();return {"items":[serialize_user(u) for u in users],"page":page,"page_size":page_size,"total":total}
@router.post("")
def create_user(data:UserCreateRequest,_:AuthContext=Depends(require_permission("users.create")),db:Session=Depends(get_db)):
    email=data.email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(status_code=409,detail="Email đã tồn tại trong hệ thống.")
    roles=load_roles(db,data.role_slugs or ["student"]);temporary_password=generate_temporary_password();raw=generate_one_time_token();now=utcnow();user=User(full_name=data.full_name.strip(),email=email,phone=data.phone,password_hash=hash_password(temporary_password),role=roles[0].slug if roles else "student",status="pending",is_active=False,must_change_password=True,roles=roles);db.add(user);db.flush();db.add(ActivationToken(user_id=user.id,token_hash=hash_one_time_token(raw),expires_at=now+timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS)));db.commit();db.refresh(user)
    frontend=os.getenv("FRONTEND_URL","http://localhost:5173");url=f"{frontend}/activate?token={raw}";sent=email_service.send(user.email,"Kích hoạt tài khoản - Hệ thống đào tạo CodeGym",f"Tài khoản của bạn đã được tạo. Mật khẩu tạm: {temporary_password}. Liên kết kích hoạt: {url}. Sau khi đăng nhập lần đầu, vui lòng đổi mật khẩu.");result=serialize_user(user);result["email_sent"]=sent;dev=os.getenv("APP_ENV","development")=="development";result["debug_temporary_password"]=temporary_password if dev else None;result["debug_activation_token"]=raw if dev else None;return result
@router.put("/{user_id}")
def update_user(user_id:int,data:UserUpdateRequest,_:AuthContext=Depends(require_permission("users.update")),db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.id==user_id).options(selectinload(User.roles)))
    if not user: raise HTTPException(status_code=404,detail="Không tìm thấy người dùng.")
    payload=data.model_dump(exclude_unset=True)
    if "email" in payload:
        email=str(payload["email"]).lower();duplicate=db.scalar(select(User).where(User.email==email,User.id!=user_id))
        if duplicate: raise HTTPException(status_code=409,detail="Email đã tồn tại trong hệ thống.")
        payload["email"]=email
    for k,v in payload.items(): setattr(user,k,v)
    db.commit();db.refresh(user);return serialize_user(user)
