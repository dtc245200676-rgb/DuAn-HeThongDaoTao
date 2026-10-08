import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import AuthContext, bearer_scheme, get_current_context
from app.core.security import SESSION_EXPIRE_MINUTES, create_access_token, decode_access_token, utcnow, verify_password
from app.db.database import get_db
from app.models.session import AuthSession
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, MessageResponse
router=APIRouter(prefix="/api/auth",tags=["Authentication"])
INVALID_LOGIN_MESSAGE="Email hoặc mật khẩu không đúng"
def _roles(user:User)->list[str]:
    result=[role.slug for role in user.roles]
    if not result and user.role: result=[user.role]
    return result
@router.post("/login",response_model=LoginResponse)
def login(data:LoginRequest,request:Request,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==data.email.lower()).options(selectinload(User.roles)))
    if user is None: raise HTTPException(status_code=401,detail=INVALID_LOGIN_MESSAGE)
    now=utcnow()
    if user.locked_until and user.locked_until>now: raise HTTPException(status_code=423,detail="Tài khoản tạm thời bị khóa 15 phút do đăng nhập sai nhiều lần.")
    if user.locked_until and user.locked_until<=now: user.failed_login_attempts=0; user.locked_until=None
    if not verify_password(data.password,user.password_hash):
        user.failed_login_attempts+=1
        if user.failed_login_attempts>=5: user.failed_login_attempts=0; user.locked_until=now+timedelta(minutes=15)
        db.commit(); raise HTTPException(status_code=401,detail=INVALID_LOGIN_MESSAGE)
    if not user.is_active or user.status=="locked": raise HTTPException(status_code=403,detail="Tài khoản đã bị khóa.")
    if user.status=="pending": raise HTTPException(status_code=403,detail="Tài khoản chưa được kích hoạt.")
    user.failed_login_attempts=0; user.locked_until=None
    session=AuthSession(id=str(uuid.uuid4()),user_id=user.id,expires_at=now+timedelta(minutes=SESSION_EXPIRE_MINUTES),last_activity_at=now,user_agent=request.headers.get("user-agent","")[:255])
    db.add(session); db.commit(); roles=_roles(user); token=create_access_token(user.id,session.id,roles)
    return LoginResponse(access_token=token,role=roles[0] if roles else user.role,roles=roles,must_change_password=user.must_change_password,message="Đăng nhập thành công")
@router.post("/refresh",response_model=LoginResponse)
def refresh_session(credentials:HTTPAuthorizationCredentials|None=Depends(bearer_scheme),db:Session=Depends(get_db)):
    if not credentials: raise HTTPException(status_code=401,detail="Thiếu phiên đăng nhập.")
    try: payload=decode_access_token(credentials.credentials,verify_exp=False)
    except ValueError as exc: raise HTTPException(status_code=401,detail="Phiên đăng nhập không hợp lệ.") from exc
    session=db.get(AuthSession,payload.get("sid")); user_id=int(payload.get("sub",0)); now=utcnow()
    if not session or session.user_id!=user_id or session.revoked_at is not None or session.expires_at<=now: raise HTTPException(status_code=401,detail={"code":"SESSION_EXPIRED","message":"Phiên đăng nhập đã hết hạn."})
    user=db.scalar(select(User).where(User.id==user_id).options(selectinload(User.roles)))
    if not user or not user.is_active or user.status!="active": raise HTTPException(status_code=403,detail="Tài khoản không còn quyền truy cập.")
    session.last_activity_at=now; session.expires_at=now+timedelta(minutes=SESSION_EXPIRE_MINUTES); db.commit(); roles=_roles(user); token=create_access_token(user.id,session.id,roles)
    return LoginResponse(access_token=token,role=roles[0] if roles else user.role,roles=roles,must_change_password=user.must_change_password,message="Phiên đăng nhập đã được gia hạn")
@router.post("/logout",response_model=MessageResponse)
def logout(context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
    context.session.revoked_at=utcnow(); db.commit(); return MessageResponse(message="Đăng xuất thành công")
@router.get("/me")
def me(context:AuthContext=Depends(get_current_context)):
    u=context.user
    return {"id":u.id,"full_name":u.full_name,"email":u.email,"phone":u.phone,"roles":context.role_slugs,"permissions":sorted(context.permissions),"must_change_password":u.must_change_password}
