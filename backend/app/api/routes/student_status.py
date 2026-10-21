from datetime import date
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.db.database import get_db
from app.models.sprint3 import ClassEnrollment,StudentProfile
from app.models.sprint4 import StudentStatusHistory
from app.models.training import TrainingClass
from app.schemas.sprint4 import StudentStatusAction,StudentTransferAction
router=APIRouter(prefix='/api/s4/student-status',tags=['S4-06 Student Status'])
def _student(db,id):
 x=db.get(StudentProfile,id)
 if not x: raise HTTPException(404,'Không tìm thấy học viên.')
 return x
def _enrollment(db,student_id,class_id):
 x=db.scalar(select(ClassEnrollment).where(ClassEnrollment.student_id==student_id,ClassEnrollment.class_id==class_id))
 if not x: raise HTTPException(404,'Học viên không thuộc lớp này.')
 return x
@router.get('/students')
def students(_:AuthContext=Depends(require_permission('training.view')),db:Session=Depends(get_db)):
 rows=db.scalars(select(StudentProfile).order_by(StudentProfile.student_code)).all();return [{'id':x.id,'student_code':x.student_code,'user_id':x.user_id} for x in rows]
@router.post('/{student_id}/reserve')
def reserve(student_id:int,data:StudentStatusAction,context:AuthContext=Depends(require_permission('training.edit')),db:Session=Depends(get_db)):
 _student(db,student_id);e=_enrollment(db,student_id,data.class_id);db.add(StudentStatusHistory(student_id=student_id,action='reserve',from_class_id=data.class_id,effective_date=data.effective_date,reason=data.reason,actor_user_id=context.user.id));
 if data.effective_date<=date.today():e.status='reserved'
 db.commit();return {'message':'Đã ghi nhận bảo lưu.','status':'reserved'}
@router.post('/{student_id}/withdraw')
def withdraw(student_id:int,data:StudentStatusAction,context:AuthContext=Depends(require_permission('training.edit')),db:Session=Depends(get_db)):
 _student(db,student_id);e=_enrollment(db,student_id,data.class_id);db.add(StudentStatusHistory(student_id=student_id,action='withdraw',from_class_id=data.class_id,effective_date=data.effective_date,reason=data.reason,actor_user_id=context.user.id));
 if data.effective_date<=date.today():e.status='withdrawn'
 db.commit();return {'message':'Đã ghi nhận thôi học.','status':'withdrawn'}
@router.post('/{student_id}/transfer')
def transfer(student_id:int,data:StudentTransferAction,context:AuthContext=Depends(require_permission('training.edit')),db:Session=Depends(get_db)):
 _student(db,student_id);old=_enrollment(db,student_id,data.from_class_id)
 if data.from_class_id==data.to_class_id: raise HTTPException(422,'Lớp chuyển đến phải khác lớp hiện tại.')
 if not db.get(TrainingClass,data.to_class_id): raise HTTPException(404,'Không tìm thấy lớp chuyển đến.')
 new=db.scalar(select(ClassEnrollment).where(ClassEnrollment.student_id==student_id,ClassEnrollment.class_id==data.to_class_id))
 if new and new.status=='active': raise HTTPException(409,'Học viên đã ở lớp chuyển đến.')
 if data.effective_date<=date.today(): old.status='transferred';new_status='active'
 else:new_status='pending_transfer'
 if new:new.status=new_status
 else:db.add(ClassEnrollment(class_id=data.to_class_id,student_id=student_id,status=new_status,enrolled_by_user_id=context.user.id))
 db.add(StudentStatusHistory(student_id=student_id,action='transfer',from_class_id=data.from_class_id,to_class_id=data.to_class_id,effective_date=data.effective_date,reason=data.reason,actor_user_id=context.user.id));db.commit();return {'message':'Đã ghi nhận chuyển lớp.','status':'transferred','to_class_id':data.to_class_id}
@router.get('/{student_id}/history')
def history(student_id:int,_:AuthContext=Depends(require_permission('training.view')),db:Session=Depends(get_db)):
 _student(db,student_id);rows=db.scalars(select(StudentStatusHistory).where(StudentStatusHistory.student_id==student_id).order_by(StudentStatusHistory.effective_date.desc(),StudentStatusHistory.id.desc())).all();return [{'id':x.id,'action':x.action,'from_class_id':x.from_class_id,'to_class_id':x.to_class_id,'effective_date':x.effective_date.isoformat(),'reason':x.reason} for x in rows]
