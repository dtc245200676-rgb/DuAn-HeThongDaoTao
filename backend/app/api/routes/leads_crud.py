from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session,selectinload
from app.api.deps import AuthContext,get_current_context,require_permission
from app.api.routes.lead_common import admissions_only,duplicate_warning,normalize_phone,serialize_lead
from app.db.database import get_db
from app.models.lead import Lead
from app.schemas.sprint2 import LeadCreate,LeadUpdate
router=APIRouter(prefix="/api/leads",tags=["S2-09 Lead CRUD"])
@router.post("")
def create_lead(data:LeadCreate,context:AuthContext=Depends(require_permission("leads.edit")),db:Session=Depends(get_db)):
    phone=normalize_phone(data.phone);lead=Lead(full_name=data.full_name.strip(),phone=phone,email=data.email.lower() if data.email else None,source=data.source,interested_program_id=data.interested_program_id,status=data.status,note=data.note);duplicate=duplicate_warning(db,phone)
    if admissions_only(context):lead.assignee_user_id=context.user.id
    db.add(lead);db.commit();db.refresh(lead);lead=db.scalar(select(Lead).where(Lead.id==lead.id).options(selectinload(Lead.interested_program),selectinload(Lead.assignee)));return {"lead":serialize_lead(lead),"duplicate_warning":duplicate}
@router.put("/{lead_id}")
def update_lead(lead_id:int,data:LeadUpdate,context:AuthContext=Depends(require_permission("leads.edit")),db:Session=Depends(get_db)):
    lead=db.scalar(select(Lead).where(Lead.id==lead_id).options(selectinload(Lead.interested_program),selectinload(Lead.assignee)))
    if not lead:raise HTTPException(404,"Không tìm thấy lead.")
    if admissions_only(context) and lead.assignee_user_id!=context.user.id:raise HTTPException(403,"Bạn chỉ được cập nhật lead được phân công cho mình.")
    payload=data.model_dump(exclude_unset=True);duplicate=None
    if "phone" in payload:payload["phone"]=normalize_phone(payload["phone"]);duplicate=duplicate_warning(db,payload["phone"],lead_id)
    if payload.get("email"):payload["email"]=str(payload["email"]).lower()
    for k,v in payload.items():setattr(lead,k,v)
    db.commit();db.refresh(lead);return {"lead":serialize_lead(lead),"duplicate_warning":duplicate}
@router.delete("/{lead_id}")
def delete_lead(lead_id:int,context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
    if "training_manager" not in context.role_slugs:raise HTTPException(403,"Chỉ Quản lý đào tạo được xóa lead.")
    lead=db.get(Lead,lead_id)
    if not lead:raise HTTPException(404,"Không tìm thấy lead.")
    db.delete(lead);db.commit();return {"message":"Đã xóa lead."}
