from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.db.database import get_db
from app.models.sprint4 import AcademicHoliday
from app.schemas.sprint4 import HolidayCreate,HolidayUpdate
router=APIRouter(prefix="/api/s4/holidays",tags=["S4-01 Holidays"])
@router.get("")
def list_holidays(_:AuthContext=Depends(require_permission("training.view")),db:Session=Depends(get_db)):
 return [{"id":x.id,"holiday_date":x.holiday_date.isoformat(),"name":x.name} for x in db.scalars(select(AcademicHoliday).order_by(AcademicHoliday.holiday_date)).all()]
@router.post("")
def create(data:HolidayCreate,context:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
 if db.scalar(select(AcademicHoliday.id).where(AcademicHoliday.holiday_date==data.holiday_date)): raise HTTPException(409,"Ngày nghỉ đã tồn tại.")
 x=AcademicHoliday(holiday_date=data.holiday_date,name=data.name.strip(),created_by_user_id=context.user.id);db.add(x);db.commit();db.refresh(x);return {"id":x.id,"holiday_date":x.holiday_date.isoformat(),"name":x.name}
@router.put("/{holiday_id}")
def update(holiday_id:int,data:HolidayUpdate,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
 x=db.get(AcademicHoliday,holiday_id)
 if not x: raise HTTPException(404,"Không tìm thấy ngày nghỉ.")
 p=data.model_dump(exclude_unset=True)
 if "holiday_date" in p and db.scalar(select(AcademicHoliday.id).where(AcademicHoliday.holiday_date==p["holiday_date"],AcademicHoliday.id!=x.id)): raise HTTPException(409,"Ngày nghỉ đã tồn tại.")
 for k,v in p.items(): setattr(x,k,v.strip() if isinstance(v,str) else v)
 db.commit();db.refresh(x);return {"id":x.id,"holiday_date":x.holiday_date.isoformat(),"name":x.name}
@router.delete("/{holiday_id}")
def delete(holiday_id:int,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
 x=db.get(AcademicHoliday,holiday_id)
 if not x: raise HTTPException(404,"Không tìm thấy ngày nghỉ.")
 db.delete(x);db.commit();return {"message":"Đã xóa ngày nghỉ."}
