from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,require_permission
from app.api.routes.sprint4_common import session_conflicts
from app.db.database import get_db
from app.models.sprint4 import ClassScheduleSession
from app.schemas.sprint4 import ConflictCheckRequest
router=APIRouter(prefix="/api/s4/conflicts",tags=["S4-02 Conflicts"])
@router.post('/check')
def check(data:ConflictCheckRequest,_:AuthContext=Depends(require_permission('training.view')),db:Session=Depends(get_db)):
 rows=session_conflicts(db,data.start_at,data.end_at,data.room_id,data.teacher_user_id,data.exclude_session_id)
 return {'has_conflict':bool(rows),'conflicts':rows}
@router.get('/sessions')
def sessions(_:AuthContext=Depends(require_permission('training.view')),db:Session=Depends(get_db)):
 rows=db.scalars(select(ClassScheduleSession).where(ClassScheduleSession.status=='scheduled').order_by(ClassScheduleSession.start_at)).all()
 return [{'id':x.id,'class_id':x.class_id,'start_at':x.start_at.isoformat(),'end_at':x.end_at.isoformat(),'room_id':x.room_id,'teacher_user_id':x.teacher_user_id} for x in rows]
