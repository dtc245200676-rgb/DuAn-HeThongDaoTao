from datetime import date,datetime,time,timedelta
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,get_current_context
from app.api.routes.sprint4_common import serialize_schedule,student_effective_state
from app.db.database import get_db
from app.models.sprint3 import ClassEnrollment,StudentProfile
from app.models.sprint4 import ClassScheduleSession
router=APIRouter(prefix='/api/s4/student-schedule',tags=['S4-05 Student Schedule'])
@router.get('/me')
def me(week_start:date|None=Query(default=None),context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 sp=db.scalar(select(StudentProfile).where(StudentProfile.user_id==context.user.id))
 if not sp: raise HTTPException(403,'Tài khoản không có hồ sơ học viên.')
 enrollments=db.scalars(select(ClassEnrollment).where(ClassEnrollment.student_id==sp.id)).all();class_ids=[x.class_id for x in enrollments]
 if not class_ids:return {'week_sessions':[],'next_session':None}
 base=week_start or date.today();start=base-timedelta(days=base.weekday());end=start+timedelta(days=7)
 candidates=db.scalars(select(ClassScheduleSession).where(ClassScheduleSession.class_id.in_(class_ids),ClassScheduleSession.status=='scheduled').order_by(ClassScheduleSession.start_at)).all()
 eligible=[x for x in candidates if student_effective_state(db,sp.id,x.class_id,x.start_at.date())=='active']
 week=[serialize_schedule(db,x) for x in eligible if start<=x.start_at.date()<end]
 now=datetime.now();nxt=next((serialize_schedule(db,x) for x in eligible if x.start_at>=now),None)
 return {'week_from':start.isoformat(),'week_to':(end-timedelta(days=1)).isoformat(),'week_sessions':week,'next_session':nxt}
