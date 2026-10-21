from datetime import date,datetime,timedelta
from sqlalchemy import select
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.role import Role
from app.models.sprint3 import ClassEnrollment,ClassSubject,ClassSubjectStaff,StudentProfile
from app.models.sprint4 import AttendanceRecord,ClassScheduleSession,UserNotification
from app.models.training import ProgramSubject,Subject,SubjectSession,TrainingClass,TrainingProgram
from app.models.user import User

def test_approved_absence_sets_excused_and_notifies(client,user_factory):
 teacher=user_factory('t408@example.com','Teacher123','teacher')
 db=SessionLocal()
 try:
  role=db.scalar(select(Role).where(Role.slug=='student'));u=User(full_name='HV',email='hv408@example.com',password_hash=hash_password('Student123'),role='student',status='active',is_active=True,roles=[role]);p=TrainingProgram(code='P408',name='P',total_duration_hours=1,standard_tuition=0,status='active');sub=Subject(code='S408',name='S',session_count=1,weight=100);db.add_all([u,p,sub]);db.flush();sp=StudentProfile(student_code='HV408',user_id=u.id);db.add(sp);db.add(ProgramSubject(program_id=p.id,subject_id=sub.id,order_index=1));lesson=SubjectSession(subject_id=sub.id,sequence=1,topic='B');db.add(lesson);c=TrainingClass(program_id=p.id,name='C408',code='C408',expected_start_date=date.today(),max_students=10,delivery_mode='offline',status='studying');db.add(c);db.flush();cs=ClassSubject(class_id=c.id,subject_id=sub.id,order_index=1);db.add(cs);db.flush();db.add(ClassSubjectStaff(class_subject_id=cs.id,user_id=teacher.id,staff_role='teacher'));db.add(ClassEnrollment(class_id=c.id,student_id=sp.id,status='active'));start=datetime.now()+timedelta(days=1);ss=ClassScheduleSession(class_id=c.id,class_subject_id=cs.id,subject_session_id=lesson.id,start_at=start,end_at=start+timedelta(hours=1),teacher_user_id=teacher.id);db.add(ss);db.commit();sid=ss.id;student_id=sp.id;student_uid=u.id
 finally:db.close()
 login=client.post('/api/auth/login',json={'email':'hv408@example.com','password':'Student123'});sh={'Authorization':f"Bearer {login.json()['access_token']}"};r=client.post('/api/s4/absence-requests',headers=sh,data={'schedule_session_id':str(sid),'reason':'Ốm'});assert r.status_code==200,r.text;rid=r.json()['id']
 login=client.post('/api/auth/login',json={'email':'t408@example.com','password':'Teacher123'});th={'Authorization':f"Bearer {login.json()['access_token']}"};r=client.patch(f'/api/s4/absence-requests/{rid}/review',headers=th,json={'status':'approved'});assert r.status_code==200,r.text
 db=SessionLocal()
 try: assert db.scalar(select(AttendanceRecord).where(AttendanceRecord.schedule_session_id==sid,AttendanceRecord.student_id==student_id)).status=='excused_absence';assert db.scalar(select(UserNotification.id).where(UserNotification.user_id==student_uid))
 finally:db.close()
