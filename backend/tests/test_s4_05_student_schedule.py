from datetime import date,datetime,timedelta
from sqlalchemy import select
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.role import Role
from app.models.sprint3 import ClassEnrollment,ClassSubject,StudentProfile
from app.models.sprint4 import ClassScheduleSession
from app.models.training import ProgramSubject,Subject,SubjectSession,TrainingClass,TrainingProgram
from app.models.user import User

def test_student_only_sees_own_class_schedule(client):
 db=SessionLocal()
 try:
  role=db.scalar(select(Role).where(Role.slug=='student'));u=User(full_name='HV',email='hv405@example.com',password_hash=hash_password('Student123'),role='student',status='active',is_active=True,roles=[role]);p=TrainingProgram(code='P405',name='P',total_duration_hours=1,standard_tuition=0,status='active');s=Subject(code='S405',name='S',session_count=1,weight=100);db.add_all([u,p,s]);db.flush();sp=StudentProfile(student_code='HV405',user_id=u.id);db.add(sp);db.add(ProgramSubject(program_id=p.id,subject_id=s.id,order_index=1));l=SubjectSession(subject_id=s.id,sequence=1,topic='B');db.add(l);c=TrainingClass(program_id=p.id,name='C405',code='C405',expected_start_date=date.today(),max_students=10,delivery_mode='offline',status='studying');db.add(c);db.flush();cs=ClassSubject(class_id=c.id,subject_id=s.id,order_index=1);db.add(cs);db.flush();db.add(ClassEnrollment(class_id=c.id,student_id=sp.id,status='active'));start=datetime.now()+timedelta(days=1);db.add(ClassScheduleSession(class_id=c.id,class_subject_id=cs.id,subject_session_id=l.id,start_at=start,end_at=start+timedelta(hours=1)));db.commit()
 finally: db.close()
 login=client.post('/api/auth/login',json={'email':'hv405@example.com','password':'Student123'});h={'Authorization':f"Bearer {login.json()['access_token']}"};r=client.get('/api/s4/student-schedule/me',headers=h);assert r.status_code==200,r.text;assert r.json()['next_session']['class_code']=='C405'
