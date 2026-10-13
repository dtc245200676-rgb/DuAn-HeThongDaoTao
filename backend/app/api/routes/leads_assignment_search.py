from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import func,or_,select
from sqlalchemy.orm import Session,selectinload
from app.api.deps import AuthContext,require_permission
from app.api.routes.lead_common import admissions_only,serialize_lead
from app.db.database import get_db
from app.models.lead import Lead,LeadAssignmentHistory
from app.models.user import User
from app.schemas.sprint2 import LeadAssignRequest
router=APIRouter(prefix="/api/leads",tags=["S2-10-11 Lead Assignment/Search"])
@router.get("")
def list_leads(q:str="",status:str|None=None,source:str|None=None,assignee_user_id:int|None=None,created_from:datetime|None=None,created_to:datetime|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),context:AuthContext=Depends(require_permission("leads.view")),db:Session=Depends(get_db)):
    stmt=select(Lead).options(selectinload(Lead.interested_program),selectinload(Lead.assignee));count_stmt=select(func.count(Lead.id));conditions=[]
    if q.strip():pattern=f"%{q.strip()}%";conditions.append(or_(Lead.full_name.like(pattern),Lead.phone.like(pattern)))
    if status:conditions.append(Lead.status==status)
    if source:conditions.append(Lead.source==source)
    if assignee_user_id:conditions.append(Lead.assignee_user_id==assignee_user_id)
    if created_from:conditions.append(Lead.created_at>=created_from)
    if created_to:conditions.append(Lead.created_at<=created_to)
    if admissions_only(context):conditions.append(Lead.assignee_user_id==context.user.id)
    if conditions:stmt=stmt.where(*conditions);count_stmt=count_stmt.where(*conditions)
    total=db.scalar(count_stmt) or 0;rows=db.scalars(stmt.order_by(Lead.id.desc()).offset((page-1)*page_size).limit(page_size)).all();return {"items":[serialize_lead(x) for x in rows],"page":page,"page_size":page_size,"total":total}
@router.post("/assign")
def assign_leads(data:LeadAssignRequest,context:AuthContext=Depends(require_permission("leads.assign")),db:Session=Depends(get_db)):
    assignee=db.get(User,data.assignee_user_id)
    if not assignee:raise HTTPException(404,"Không tìm thấy người được phân công.")
    if "admissions" not in {r.slug for r in assignee.roles}:raise HTTPException(422,"Lead chỉ được phân công cho người có vai trò Tuyển sinh.")
    leads=db.scalars(select(Lead).where(Lead.id.in_(set(data.lead_ids)))).all()
    if len(leads)!=len(set(data.lead_ids)):raise HTTPException(404,"Có lead không tồn tại.")
    for lead in leads:
        old=lead.assignee_user_id;lead.assignee_user_id=assignee.id;db.add(LeadAssignmentHistory(lead_id=lead.id,from_user_id=old,to_user_id=assignee.id,actor_user_id=context.user.id))
    db.commit();return {"message":"Đã phân công lead.","count":len(leads),"assignee_user_id":assignee.id}
@router.get("/{lead_id}/assignment-history")
def assignment_history(lead_id:int,context:AuthContext=Depends(require_permission("leads.view")),db:Session=Depends(get_db)):
    lead=db.get(Lead,lead_id)
    if not lead:raise HTTPException(404,"Không tìm thấy lead.")
    if admissions_only(context) and lead.assignee_user_id!=context.user.id:raise HTTPException(403,"Bạn chỉ được xem lịch sử lead được phân công cho mình.")
    rows=db.scalars(select(LeadAssignmentHistory).where(LeadAssignmentHistory.lead_id==lead_id).options(selectinload(LeadAssignmentHistory.from_user),selectinload(LeadAssignmentHistory.to_user),selectinload(LeadAssignmentHistory.actor_user)).order_by(LeadAssignmentHistory.id.desc())).all();return [{"id":x.id,"from_user_id":x.from_user_id,"from_user":x.from_user.full_name if x.from_user else None,"to_user_id":x.to_user_id,"to_user":x.to_user.full_name if x.to_user else None,"actor_user":x.actor_user.full_name if x.actor_user else None,"created_at":x.created_at} for x in rows]
