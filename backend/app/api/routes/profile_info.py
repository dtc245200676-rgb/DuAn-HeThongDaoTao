from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,get_current_context
from app.api.routes.profile_common import serialize_profile
from app.db.database import get_db
from app.schemas.sprint2 import ProfileUpdate
router=APIRouter(prefix="/api/profile",tags=["S2-02 Profile"])
@router.get("")
def get_profile(context:AuthContext=Depends(get_current_context)): return serialize_profile(context.user)
@router.put("")
def update_profile(data:ProfileUpdate,context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
    context.user.full_name=data.full_name.strip();context.user.phone=data.phone;context.user.date_of_birth=data.date_of_birth;context.user.address=data.address.strip() if data.address else None
    db.commit();db.refresh(context.user);return serialize_profile(context.user)
