from calendar import monthrange
from datetime import date,timedelta,datetime,time
from fastapi import APIRouter,Depends,Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.api.routes.sprint4_common import serialize_schedule
from app.db.database import get_db
from app.models.sprint4 import ClassScheduleSession
router=APIRouter(prefix='/api/s4/calendar',tags=['S4-04 Calendar'])
@router.get('/events')
def events(view:str='week',anchor_date:date=Query(default_factory=date.today),class_id:int|None=None,teacher_user_id:int|None=None,room_id:int|None=None,_:AuthContext=Depends(require_permission('training.view')),db:Session=Depends(get_db)):
 if view=='month': start=anchor_date.replace(day=1);end=start+timedelta(days=monthrange(start.year,start.month)[1])
 else: start=anchor_date-timedelta(days=anchor_date.weekday());end=start+timedelta(days=7)
 stmt=select(ClassScheduleSession).where(ClassScheduleSession.start_at>=datetime.combine(start,time.min),ClassScheduleSession.start_at<datetime.combine(end,time.min))
 if class_id: stmt=stmt.where(ClassScheduleSession.class_id==class_id)
 if teacher_user_id: stmt=stmt.where(ClassScheduleSession.teacher_user_id==teacher_user_id)
 if room_id: stmt=stmt.where(ClassScheduleSession.room_id==room_id)
 rows=db.scalars(stmt.order_by(ClassScheduleSession.start_at)).all()
 return {'view':view,'from':start.isoformat(),'to':(end-timedelta(days=1)).isoformat(),'events':[serialize_schedule(db,x) for x in rows]}
