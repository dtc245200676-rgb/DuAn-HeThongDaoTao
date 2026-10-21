from datetime import datetime
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter,Depends,File,Form,HTTPException,UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,get_current_context
from app.api.routes.sprint4_common import eligible_students_for_session,notify,serialize_schedule
from app.db.database import get_db
from app.models.sprint3 import ClassSubjectStaff,StudentProfile
from app.models.sprint4 import AbsenceRequest,AttendanceAuditLog,AttendanceRecord,ClassScheduleSession
from app.schemas.sprint4 import AbsenceReviewRequest
router=APIRouter(prefix='/api/s4/absence-requests',tags=['S4-08 Absence Requests'])
UPLOAD=Path('uploads/absence_requests');UPLOAD.mkdir(parents=True,exist_ok=True)
def _student(db,user_id):
 sp=db.scalar(select(StudentProfile).where(StudentProfile.user_id==user_id))
 if not sp: raise HTTPException(403,'Chỉ học viên có hồ sơ mới gửi đơn xin phép.')
 return sp
@router.get('/my-sessions')
def my_sessions(context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 sp=_student(db,context.user.id);rows=db.scalars(select(ClassScheduleSession).where(ClassScheduleSession.status=='scheduled',ClassScheduleSession.start_at>=datetime.now()).order_by(ClassScheduleSession.start_at)).all();rows=[x for x in rows if sp.id in {s.id for s in eligible_students_for_session(db,x)}];return [serialize_schedule(db,x) for x in rows]
@router.post('')
async def create(schedule_session_id:int=Form(...),reason:str=Form(...),evidence:UploadFile|None=File(default=None),context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 sp=_student(db,context.user.id);session=db.get(ClassScheduleSession,schedule_session_id)
 if not session: raise HTTPException(404,'Không tìm thấy buổi học.')
 if sp.id not in {s.id for s in eligible_students_for_session(db,session)}: raise HTTPException(403,'Buổi học không thuộc lớp của bạn.')
 if db.scalar(select(AbsenceRequest.id).where(AbsenceRequest.schedule_session_id==session.id,AbsenceRequest.student_id==sp.id,AbsenceRequest.status=='pending')): raise HTTPException(409,'Bạn đã có đơn đang chờ duyệt cho buổi này.')
 path=None
 if evidence and evidence.filename:
  suffix=Path(evidence.filename).suffix.lower();path=UPLOAD/f'{uuid4().hex}{suffix}';path.write_bytes(await evidence.read())
 x=AbsenceRequest(schedule_session_id=session.id,student_id=sp.id,reason=reason.strip(),evidence_path=str(path).replace('\\','/') if path else None);db.add(x);db.commit();db.refresh(x);return {'id':x.id,'status':x.status,'message':'Đã gửi đơn xin phép.'}
@router.get('/mine')
def mine(context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 sp=_student(db,context.user.id);rows=db.scalars(select(AbsenceRequest).where(AbsenceRequest.student_id==sp.id).order_by(AbsenceRequest.created_at.desc())).all();return [{'id':x.id,'schedule_session_id':x.schedule_session_id,'reason':x.reason,'evidence_path':x.evidence_path,'status':x.status,'review_reason':x.review_reason,'created_at':x.created_at.isoformat()} for x in rows]
@router.get('/review')
def review_list(context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 rows=db.scalars(select(AbsenceRequest).where(AbsenceRequest.status=='pending').order_by(AbsenceRequest.created_at)).all();out=[]
 for x in rows:
  s=db.get(ClassScheduleSession,x.schedule_session_id)
  allowed={'system_admin','training_manager'}&set(context.role_slugs)
  if not allowed and 'teacher' in context.role_slugs:
   allowed=bool(db.scalar(select(ClassSubjectStaff.id).where(ClassSubjectStaff.class_subject_id==s.class_subject_id,ClassSubjectStaff.user_id==context.user.id,ClassSubjectStaff.staff_role=='teacher')))
  if allowed:out.append({'id':x.id,'schedule_session_id':x.schedule_session_id,'student_id':x.student_id,'reason':x.reason,'evidence_path':x.evidence_path,'session':serialize_schedule(db,s)})
 return out
@router.patch('/{request_id}/review')
def review(request_id:int,data:AbsenceReviewRequest,context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
 x=db.get(AbsenceRequest,request_id)
 if not x: raise HTTPException(404,'Không tìm thấy đơn.')
 if x.status!='pending': raise HTTPException(409,'Đơn đã được xử lý.')
 s=db.get(ClassScheduleSession,x.schedule_session_id);allowed=bool({'system_admin','training_manager'}&set(context.role_slugs))
 if not allowed and 'teacher' in context.role_slugs: allowed=bool(db.scalar(select(ClassSubjectStaff.id).where(ClassSubjectStaff.class_subject_id==s.class_subject_id,ClassSubjectStaff.user_id==context.user.id,ClassSubjectStaff.staff_role=='teacher')))
 if not allowed: raise HTTPException(403,'Bạn không có quyền duyệt đơn này.')
 x.status=data.status;x.review_reason=data.reason;x.reviewer_user_id=context.user.id;x.reviewed_at=datetime.now()
 if data.status=='approved':
  rec=db.scalar(select(AttendanceRecord).where(AttendanceRecord.schedule_session_id==s.id,AttendanceRecord.student_id==x.student_id));old=rec.status if rec else None
  if not rec:rec=AttendanceRecord(schedule_session_id=s.id,student_id=x.student_id,status='excused_absence',note='Đơn xin phép đã được duyệt',marked_by_user_id=context.user.id,updated_by_user_id=context.user.id);db.add(rec);db.flush()
  else:rec.status='excused_absence';rec.updated_by_user_id=context.user.id;rec.updated_at=datetime.now()
  db.add(AttendanceAuditLog(attendance_id=rec.id,from_status=old,to_status='excused_absence',reason='Đơn xin phép được duyệt',actor_user_id=context.user.id))
 sp=db.get(StudentProfile,x.student_id);notify(db,sp.user_id,'Kết quả đơn xin phép',f'Đơn xin phép của bạn đã được {"duyệt" if data.status=="approved" else "từ chối"}.','/absence-requests');db.commit();return {'message':'Đã xử lý đơn.','status':x.status}
