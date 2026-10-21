from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.api.routes.sprint4_common import notify,serialize_schedule,session_conflicts
from app.db.database import get_db
from app.models.sprint3 import ClassEnrollment,StudentProfile
from app.models.sprint4 import AttendanceRecord,ClassScheduleSession,ScheduleChangeHistory
from app.models.user import User
from app.schemas.sprint4 import ScheduleSessionChange
router=APIRouter(prefix='/api/s4/schedule-changes',tags=['S4-03 Session Changes'])
@router.get('/sessions')
def list_sessions(_:AuthContext=Depends(require_permission('training.view')),db:Session=Depends(get_db)):
 return [serialize_schedule(db,x) for x in db.scalars(select(ClassScheduleSession).order_by(ClassScheduleSession.start_at)).all()]
@router.patch('/sessions/{session_id}')
def change(session_id:int,data:ScheduleSessionChange,context:AuthContext=Depends(require_permission('training.edit')),db:Session=Depends(get_db)):
 x=db.get(ClassScheduleSession,session_id)
 if not x: raise HTTPException(404,'Không tìm thấy buổi học.')
 if db.scalar(select(AttendanceRecord.id).where(AttendanceRecord.schedule_session_id==x.id)): raise HTTPException(409,'Không thể sửa hoặc hủy buổi đã điểm danh.')
 p=data.model_dump(exclude_unset=True);old_start,old_end,old_room,old_teacher=x.start_at,x.end_at,x.room_id,x.teacher_user_id
 new_start=p.get('start_at',x.start_at);new_end=p.get('end_at',x.end_at);new_room=p.get('room_id',x.room_id);new_teacher=p.get('teacher_user_id',x.teacher_user_id)
 conflicts=session_conflicts(db,new_start,new_end,new_room,new_teacher,x.id)
 if conflicts and not data.force_override: raise HTTPException(409,detail={'message':'Buổi học mới bị xung đột.','conflicts':conflicts})
 if conflicts and data.force_override and not ({'system_admin','training_manager'}&set(context.role_slugs)): raise HTTPException(403,'Chỉ Quản lý đào tạo được xác nhận ghi đè.')
 for key in ['start_at','end_at','room_id','teacher_user_id']:
  if key in p: setattr(x,key,p[key])
 action='rescheduled'
 if p.get('status')=='cancelled': x.status='cancelled';x.cancellation_reason=(data.reason or '').strip();action='cancelled'
 elif p.get('status')=='scheduled': x.status='scheduled';x.cancellation_reason=None
 x.conflict_override=bool(conflicts)
 db.add(ScheduleChangeHistory(schedule_session_id=x.id,action=action,old_start_at=old_start,old_end_at=old_end,old_room_id=old_room,old_teacher_user_id=old_teacher,reason=data.reason,actor_user_id=context.user.id))
 # notify enrolled students and affected teacher
 enrollments=db.scalars(select(ClassEnrollment).where(ClassEnrollment.class_id==x.class_id,ClassEnrollment.status=='active')).all()
 for enr in enrollments:
  sp=db.get(StudentProfile,enr.student_id)
  if sp: notify(db,sp.user_id,'Thay đổi lịch học',f'Buổi học lớp của bạn đã được {"hủy" if action=="cancelled" else "thay đổi"}.','/my-schedule')
 teacher_ids={tid for tid in [old_teacher,x.teacher_user_id] if tid}
 for tid in teacher_ids: notify(db,tid,'Thay đổi lịch giảng','Một buổi giảng của bạn vừa được thay đổi.','/training/calendar')
 db.commit();db.refresh(x);return serialize_schedule(db,x)
