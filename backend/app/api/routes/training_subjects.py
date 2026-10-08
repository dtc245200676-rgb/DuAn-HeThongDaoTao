from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.api.routes.training_common import subject_dict
from app.db.database import get_db
from app.models.training import ProgramSubject,Subject,SubjectSession,TrainingClass,TrainingProgram
from app.schemas.sprint2 import SubjectCreate,SubjectUpdate
router=APIRouter(prefix="/api/training",tags=["S2-05 Subjects"])
@router.get("/subjects")
def list_subjects(_:AuthContext=Depends(require_permission("training.view")),db:Session=Depends(get_db)): return [subject_dict(x) for x in db.scalars(select(Subject).order_by(Subject.id.desc())).all()]
@router.post("/subjects")
def create_subject(data:SubjectCreate,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    code=data.code.strip().upper()
    if db.scalar(select(Subject.id).where(Subject.code==code)): raise HTTPException(409,"Mã môn học đã tồn tại.")
    s=Subject(code=code,**data.model_dump(exclude={"code"}));db.add(s);db.commit();db.refresh(s);return subject_dict(s)
@router.put("/subjects/{subject_id}")
def update_subject(subject_id:int,data:SubjectUpdate,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    s=db.get(Subject,subject_id)
    if not s: raise HTTPException(404,"Không tìm thấy môn học.")
    payload=data.model_dump(exclude_unset=True)
    if "session_count" in payload:
        current=db.scalar(select(func.count(SubjectSession.id)).where(SubjectSession.subject_id==subject_id)) or 0
        if payload["session_count"]<current: raise HTTPException(409,"Số buổi không thể nhỏ hơn số buổi đã khai báo.")
    for k,v in payload.items():setattr(s,k,v)
    db.commit();db.refresh(s);return subject_dict(s)
@router.delete("/subjects/{subject_id}")
def delete_subject(subject_id:int,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    s=db.get(Subject,subject_id)
    if not s:raise HTTPException(404,"Không tìm thấy môn học.")
    class_use=db.scalar(select(func.count(TrainingClass.id)).join(TrainingProgram,TrainingProgram.id==TrainingClass.program_id).join(ProgramSubject,ProgramSubject.program_id==TrainingProgram.id).where(ProgramSubject.subject_id==subject_id)) or 0
    if class_use:raise HTTPException(409,"Môn học đã được sử dụng trong lớp học nên không thể xóa.")
    db.delete(s);db.commit();return {"message":"Đã xóa môn học."}
