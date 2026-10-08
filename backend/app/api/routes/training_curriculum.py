from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session,selectinload
from app.api.deps import AuthContext,require_permission
from app.api.routes.training_common import subject_dict
from app.db.database import get_db
from app.models.training import ProgramSubject,Subject,TrainingProgram
from app.schemas.sprint2 import ProgramSubjectAdd,ProgramSubjectPrerequisite,ProgramSubjectReorder
router=APIRouter(prefix="/api/training",tags=["S2-06 Curriculum"])
@router.get("/programs/{program_id}/subjects")
def program_subjects(program_id:int,_:AuthContext=Depends(require_permission("training.view")),db:Session=Depends(get_db)):
    rows=db.scalars(select(ProgramSubject).where(ProgramSubject.program_id==program_id).options(selectinload(ProgramSubject.subject),selectinload(ProgramSubject.prerequisite_subject)).order_by(ProgramSubject.order_index)).all();return [{"id":r.id,"order_index":r.order_index,"subject":subject_dict(r.subject),"prerequisite_subject_id":r.prerequisite_subject_id,"prerequisite_subject":subject_dict(r.prerequisite_subject) if r.prerequisite_subject else None} for r in rows]
@router.post("/programs/{program_id}/subjects")
def add_program_subject(program_id:int,data:ProgramSubjectAdd,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    if not db.get(TrainingProgram,program_id):raise HTTPException(404,"Không tìm thấy chương trình.")
    if not db.get(Subject,data.subject_id):raise HTTPException(404,"Không tìm thấy môn học.")
    if db.scalar(select(ProgramSubject.id).where(ProgramSubject.program_id==program_id,ProgramSubject.subject_id==data.subject_id)):raise HTTPException(409,"Môn học đã có trong chương trình.")
    if data.prerequisite_subject_id and not db.scalar(select(ProgramSubject.id).where(ProgramSubject.program_id==program_id,ProgramSubject.subject_id==data.prerequisite_subject_id)):raise HTTPException(422,"Môn tiên quyết phải thuộc cùng chương trình.")
    max_order=db.scalar(select(func.max(ProgramSubject.order_index)).where(ProgramSubject.program_id==program_id)) or 0;row=ProgramSubject(program_id=program_id,subject_id=data.subject_id,order_index=max_order+1,prerequisite_subject_id=data.prerequisite_subject_id);db.add(row);db.commit();return {"message":"Đã thêm môn học vào chương trình.","id":row.id}
@router.delete("/programs/{program_id}/subjects/{subject_id}")
def remove_program_subject(program_id:int,subject_id:int,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    row=db.scalar(select(ProgramSubject).where(ProgramSubject.program_id==program_id,ProgramSubject.subject_id==subject_id))
    if not row:raise HTTPException(404,"Môn học không có trong chương trình.")
    if db.scalar(select(func.count(ProgramSubject.id)).where(ProgramSubject.program_id==program_id,ProgramSubject.prerequisite_subject_id==subject_id)) or 0:raise HTTPException(409,"Không thể gỡ môn đang là tiên quyết của môn khác.")
    db.delete(row);db.commit();rows=db.scalars(select(ProgramSubject).where(ProgramSubject.program_id==program_id).order_by(ProgramSubject.order_index)).all()
    for idx,x in enumerate(rows,1):x.order_index=idx
    db.commit();return {"message":"Đã gỡ môn khỏi chương trình."}
@router.put("/programs/{program_id}/subjects/reorder")
def reorder_program_subjects(program_id:int,data:ProgramSubjectReorder,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    rows=db.scalars(select(ProgramSubject).where(ProgramSubject.program_id==program_id)).all();existing={r.subject_id:r for r in rows}
    if set(data.subject_ids)!=set(existing):raise HTTPException(422,"Danh sách sắp xếp phải chứa đúng các môn của chương trình.")
    position={sid:i for i,sid in enumerate(data.subject_ids,1)}
    for r in rows:
        if r.prerequisite_subject_id is not None and position[r.prerequisite_subject_id]>=position[r.subject_id]:raise HTTPException(422,"Thứ tự mới làm môn tiên quyết đứng sau môn phụ thuộc.")
    for idx,sid in enumerate(data.subject_ids,1):existing[sid].order_index=-idx
    db.flush()
    for idx,sid in enumerate(data.subject_ids,1):existing[sid].order_index=idx
    db.commit();return {"message":"Đã lưu thứ tự môn học.","subject_ids":data.subject_ids}
@router.put("/programs/{program_id}/subjects/{subject_id}/prerequisite")
def set_prerequisite(program_id:int,subject_id:int,data:ProgramSubjectPrerequisite,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    row=db.scalar(select(ProgramSubject).where(ProgramSubject.program_id==program_id,ProgramSubject.subject_id==subject_id))
    if not row:raise HTTPException(404,"Môn học không có trong chương trình.")
    if data.prerequisite_subject_id==subject_id:raise HTTPException(422,"Môn học không thể là tiên quyết của chính nó.")
    if data.prerequisite_subject_id is not None:
        prereq=db.scalar(select(ProgramSubject).where(ProgramSubject.program_id==program_id,ProgramSubject.subject_id==data.prerequisite_subject_id))
        if not prereq:raise HTTPException(422,"Môn tiên quyết phải thuộc cùng chương trình.")
        if prereq.order_index>=row.order_index:raise HTTPException(422,"Môn tiên quyết phải đứng trước môn hiện tại.")
    row.prerequisite_subject_id=data.prerequisite_subject_id;db.commit();return {"message":"Đã cập nhật môn tiên quyết."}
