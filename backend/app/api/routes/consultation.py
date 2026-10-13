import time
from collections import defaultdict,deque
from fastapi import APIRouter,Depends,HTTPException,Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.routes.lead_common import duplicate_warning,normalize_phone
from app.db.database import get_db
from app.models.lead import Lead
from app.models.training import TrainingProgram
from app.schemas.sprint2 import PublicLeadCreate
router=APIRouter(tags=["S2-08 Consultation"]);_hits:dict[str,deque[float]]=defaultdict(deque);LIMIT=5;WINDOW=60
@router.get("/api/training/public-programs")
def public_programs(db:Session=Depends(get_db)):
    rows=db.scalars(select(TrainingProgram).where(TrainingProgram.status=="active").order_by(TrainingProgram.name)).all();return [{"id":x.id,"code":x.code,"name":x.name} for x in rows]
@router.post("/api/leads/public")
def public_consultation(data:PublicLeadCreate,request:Request,db:Session=Depends(get_db)):
    if data.website: return {"message":"Cảm ơn bạn đã đăng ký tư vấn.","commitment":"Đội ngũ tư vấn sẽ liên hệ lại trong vòng 24 giờ."}
    ip=request.client.host if request.client else "unknown";now=time.time();q=_hits[ip]
    while q and q[0]<now-WINDOW:q.popleft()
    if len(q)>=LIMIT: raise HTTPException(429,"Bạn gửi yêu cầu quá nhanh. Vui lòng thử lại sau ít phút.")
    q.append(now);phone=normalize_phone(data.phone);duplicate=duplicate_warning(db,phone);lead=Lead(full_name=data.full_name.strip(),phone=phone,email=data.email.lower() if data.email else None,source=data.source or "website",interested_program_id=data.interested_program_id,status="new");db.add(lead);db.commit();db.refresh(lead)
    return {"message":"Cảm ơn bạn đã đăng ký tư vấn.","commitment":"Đội ngũ tư vấn sẽ liên hệ lại trong vòng 24 giờ.","lead_id":lead.id,"duplicate_warning":duplicate}
