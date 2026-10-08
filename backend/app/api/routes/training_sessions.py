from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.api.routes.training_common import session_dict
from app.db.database import get_db
from app.models.training import Subject,SubjectSession
from app.schemas.sprint2 import CloneSessionsRequest,SubjectSessionCreate
router=APIRouter(prefix="/api/training",tags=["S2-07 Sessions"])
@router.get("/subjects/{subject_id}/sessions")
def list_sessions(subject_id:int,_:AuthContext=Depends(require_permission("training.view")),db:Session=Depends(get_db)):return [session_dict(x) for x in db.scalars(select(SubjectSession).where(SubjectSession.subject_id==subject_id).order_by(SubjectSession.sequence)).all()]
@router.post("/subjects/{subject_id}/sessions")
def create_session(subject_id:int,data:SubjectSessionCreate,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    subject=db.get(Subject,subject_id)
    if not subject:raise HTTPException(404,"Không tìm thấy môn học.")
    count=db.scalar(select(func.count(SubjectSession.id)).where(SubjectSession.subject_id==subject_id)) or 0
    if count>=subject.session_count:raise HTTPException(409,"Số buổi khai báo không được vượt quá số buổi của môn học.")
    if data.sequence>subject.session_count:raise HTTPException(422,"Số thứ tự buổi vượt quá số buổi của môn học.")
    if db.scalar(select(SubjectSession.id).where(SubjectSession.subject_id==subject_id,SubjectSession.sequence==data.sequence)):raise HTTPException(409,"Số thứ tự buổi đã tồn tại.")
    x=SubjectSession(subject_id=subject_id,**data.model_dump());db.add(x);db.commit();db.refresh(x);return session_dict(x)
@router.post("/subjects/{subject_id}/sessions/clone")
def clone_sessions(subject_id:int,data:CloneSessionsRequest,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    target=db.get(Subject,subject_id);source=db.get(Subject,data.source_subject_id)
    if not target or not source:raise HTTPException(404,"Không tìm thấy môn học nguồn hoặc đích.")
    rows=db.scalars(select(SubjectSession).where(SubjectSession.subject_id==source.id).order_by(SubjectSession.sequence)).all()
    if len(rows)>target.session_count:raise HTTPException(409,"Số buổi của môn nguồn vượt quá số buổi cho phép của môn đích.")
    for x in db.scalars(select(SubjectSession).where(SubjectSession.subject_id==target.id)).all():db.delete(x)
    db.flush()
    for x in rows:db.add(SubjectSession(subject_id=target.id,sequence=x.sequence,topic=x.topic,objective=x.objective))
    db.commit();return {"message":"Đã nhân bản danh sách buổi học.","count":len(rows)}
