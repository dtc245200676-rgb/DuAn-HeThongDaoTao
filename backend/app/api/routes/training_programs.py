from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.api.routes.training_common import program_dict
from app.db.database import get_db
from app.models.training import TrainingClass,TrainingProgram
from app.schemas.sprint2 import TrainingProgramCreate,TrainingProgramUpdate
router=APIRouter(prefix="/api/training",tags=["S2-04 Programs"])
@router.get("/programs")
def list_programs(_:AuthContext=Depends(require_permission("training.view")),db:Session=Depends(get_db)): return [program_dict(x) for x in db.scalars(select(TrainingProgram).order_by(TrainingProgram.id.desc())).all()]
@router.post("/programs")
def create_program(data:TrainingProgramCreate,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    code=data.code.strip().upper()
    if db.scalar(select(TrainingProgram.id).where(TrainingProgram.code==code)): raise HTTPException(409,"Mã chương trình đã tồn tại.")
    p=TrainingProgram(code=code,name=data.name.strip(),description=data.description,total_duration_hours=data.total_duration_hours,standard_tuition=data.standard_tuition,status=data.status);db.add(p);db.commit();db.refresh(p);return program_dict(p)
@router.put("/programs/{program_id}")
def update_program(program_id:int,data:TrainingProgramUpdate,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    p=db.get(TrainingProgram,program_id)
    if not p: raise HTTPException(404,"Không tìm thấy chương trình.")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(p,k,v)
    db.commit();db.refresh(p);return program_dict(p)
@router.delete("/programs/{program_id}")
def delete_program(program_id:int,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    p=db.get(TrainingProgram,program_id)
    if not p: raise HTTPException(404,"Không tìm thấy chương trình.")
    running=db.scalar(select(func.count(TrainingClass.id)).where(TrainingClass.program_id==program_id,TrainingClass.status.in_(["active","running"]))) or 0
    if running: raise HTTPException(409,"Chương trình đang có lớp chạy, không được xóa; hãy chuyển trạng thái sang ngừng áp dụng.")
    db.delete(p);db.commit();return {"message":"Đã xóa chương trình."}
