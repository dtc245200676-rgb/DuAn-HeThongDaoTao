from datetime import date,datetime,timedelta
from sqlalchemy import select
from app.db.database import SessionLocal
from app.core.security import hash_password
from app.models.role import Role
from app.models.sprint3 import ClassEnrollment,ClassSubject,StudentProfile
from app.models.sprint4 import AttendanceRecord,ClassScheduleSession,UserNotification
from app.models.training import ProgramSubject,Subject,SubjectSession,TrainingClass,TrainingProgram
from app.models.user import User

def test_cancel_notifies_and_attended_session_locked(client,admin_headers):
 db=SessionLocal()
 try:
  role=db.scalar(select(Role).where(Role.slug=='student'));u=User(full_name='HV',email='hv403@example.com',password_hash=hash_password('Student123'),role='student',status='active',is_active=True,roles=[role]);p=TrainingProgram(code='P403',name='P',total_duration_hours=1,standard_tuition=0,status='active');s=Subject(code='S403',name='S',session_count=2,weight=100);db.add_all([u,p,s]);db.flush();sp=StudentProfile(student_code='HV403',user_id=u.id);db.add(sp);db.add(ProgramSubject(program_id=p.id,subject_id=s.id,order_index=1));l1=SubjectSession(subject_id=s.id,sequence=1,topic='B1');l2=SubjectSession(subject_id=s.id,sequence=2,topic='B2');db.add_all([l1,l2]);c=TrainingClass(program_id=p.id,name='C403',code='C403',expected_start_date=date.today(),max_students=10,delivery_mode='offline',status='studying');db.add(c);db.flush();cs=ClassSubject(class_id=c.id,subject_id=s.id,order_index=1);db.add(cs);db.flush();db.add(ClassEnrollment(class_id=c.id,student_id=sp.id,status='active'));start=datetime.now()+timedelta(days=2);a=ClassScheduleSession(class_id=c.id,class_subject_id=cs.id,subject_session_id=l1.id,start_at=start,end_at=start+timedelta(hours=1));b=ClassScheduleSession(class_id=c.id,class_subject_id=cs.id,subject_session_id=l2.id,start_at=start+timedelta(days=1),end_at=start+timedelta(days=1,hours=1));db.add_all([a,b]);db.flush();db.add(AttendanceRecord(schedule_session_id=b.id,student_id=sp.id,status='present'));db.commit();aid=a.id;bid=b.id;uid=u.id
 finally: db.close()
 r=client.patch(f'/api/s4/schedule-changes/sessions/{aid}',headers=admin_headers,json={'status':'cancelled','reason':'Giảng viên bận'});assert r.status_code==200,r.text;assert r.json()['status']=='cancelled'
 db=SessionLocal()
 try: assert db.scalar(select(UserNotification.id).where(UserNotification.user_id==uid))
 finally: db.close()
 assert client.patch(f'/api/s4/schedule-changes/sessions/{bid}',headers=admin_headers,json={'status':'cancelled','reason':'x'}).status_code==409
