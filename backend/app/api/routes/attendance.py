from datetime import date,datetime,timedelta
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,get_current_context
from app.api.routes.sprint4_common import can_manage_past_attendance,eligible_students_for_session,serialize_schedule
from app.db.database import get_db
from app.models.sprint3 import ClassSubjectStaff
from app.models.sprint4 import AttendanceAuditLog,AttendanceRecord,ClassScheduleSession
from app.models.user import User
from app.schemas.sprint4 import AttendanceSaveRequest
router=APIRouter(prefix='/api/s4/attendance',tags=['S4-07 Attendance'])
def _check_access(db,session,context,editing=False):
 if can_manage_past_attendance(context):return
 if 'teacher' not in context.role_slugs: raise HTTPException(403,'Chỉ giảng viên hoặc Quản lý đào tạo được điểm danh.')
 assigned=db.scalar(select(ClassSubjectStaff.id).where(ClassSubjectStaff.class_subject_id==session.class_subject_id,ClassSubjectStaff.user_id==context.user.id,ClassSubjectStaff.staff_role=='teacher'))
 if not assigned: raise HTTPException(403,'Bạn không được phân công giảng dạy buổi này.')
 if session.start_at.date()!=date.today(): raise HTTPException(403,'Giảng viên chỉ được điểm danh buổi của ngày hôm nay; sửa buổi quá khứ cần quyền Quản lý đào tạo.')
@router.get('/sessions')
def sessions(context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 stmt=select(ClassScheduleSession).where(ClassScheduleSession.status=='scheduled').order_by(ClassScheduleSession.start_at)
 rows=db.scalars(stmt).all()
 if 'teacher' in context.role_slugs and not can_manage_past_attendance(context):
  ids=set(db.scalars(select(ClassSubjectStaff.class_subject_id).where(ClassSubjectStaff.user_id==context.user.id,ClassSubjectStaff.staff_role=='teacher')).all());rows=[x for x in rows if x.class_subject_id in ids]
 return [serialize_schedule(db,x) for x in rows]
@router.get('/sessions/{session_id}/roster')
def roster(session_id:int,context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 s=db.get(ClassScheduleSession,session_id)
 if not s:raise HTTPException(404,'Không tìm thấy buổi học.')
 _check_access(db,s,context)
 students=eligible_students_for_session(db,s);records={x.student_id:x for x in db.scalars(select(AttendanceRecord).where(AttendanceRecord.schedule_session_id==s.id)).all()}
 out=[]
 for sp in students:
  u=db.get(User,sp.user_id);r=records.get(sp.id);out.append({'student_id':sp.id,'student_code':sp.student_code,'full_name':u.full_name if u else sp.student_code,'status':r.status if r else 'present','note':r.note if r else None})
 return {'session':serialize_schedule(db,s),'students':out}
@router.post('/sessions/{session_id}')
def save(session_id:int,data:AttendanceSaveRequest,context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 s=db.get(ClassScheduleSession,session_id)
 if not s:raise HTTPException(404,'Không tìm thấy buổi học.')
 _check_access(db,s,context,True)
 if s.start_at.date()<date.today() and can_manage_past_attendance(context) and not (data.correction_reason or '').strip(): raise HTTPException(422,'Sửa điểm danh buổi quá khứ phải ghi lý do điều chỉnh.')
 eligible={x.id for x in eligible_students_for_session(db,s)}
 for item in data.items:
  if item.student_id not in eligible: raise HTTPException(422,f'Học viên {item.student_id} không thuộc danh sách điểm danh của buổi này.')
  rec=db.scalar(select(AttendanceRecord).where(AttendanceRecord.schedule_session_id==s.id,AttendanceRecord.student_id==item.student_id));old=rec.status if rec else None
  if not rec: rec=AttendanceRecord(schedule_session_id=s.id,student_id=item.student_id,status=item.status,note=item.note,marked_by_user_id=context.user.id,updated_by_user_id=context.user.id);db.add(rec);db.flush()
  else: rec.status=item.status;rec.note=item.note;rec.updated_by_user_id=context.user.id;rec.updated_at=datetime.now()
  db.add(AttendanceAuditLog(attendance_id=rec.id,from_status=old,to_status=item.status,reason=data.correction_reason,actor_user_id=context.user.id))
 db.commit();return {'message':'Đã lưu điểm danh.','count':len(data.items)}
