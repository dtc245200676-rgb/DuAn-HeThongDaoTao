from datetime import date,datetime,timedelta
from app.db.database import SessionLocal
from app.models.sprint3 import ClassSubject
from app.models.sprint4 import ClassScheduleSession
from app.models.training import ProgramSubject,Subject,SubjectSession,TrainingClass,TrainingProgram

def test_detect_teacher_and_room_conflicts(client,admin_headers,user_factory):
 teacher=user_factory('t402@example.com','Teacher123','teacher')
 db=SessionLocal()
 try:
  p=TrainingProgram(code='P402',name='P',total_duration_hours=1,standard_tuition=0,status='active');s=Subject(code='S402',name='S',session_count=1,weight=100);db.add_all([p,s]);db.flush();db.add(ProgramSubject(program_id=p.id,subject_id=s.id,order_index=1));lesson=SubjectSession(subject_id=s.id,sequence=1,topic='B1');db.add(lesson);c=TrainingClass(program_id=p.id,name='C402',code='C402',expected_start_date=date.today(),max_students=10,delivery_mode='offline',status='studying');db.add(c);db.flush();cs=ClassSubject(class_id=c.id,subject_id=s.id,order_index=1);db.add(cs);db.flush();start=datetime.now()+timedelta(days=2);row=ClassScheduleSession(class_id=c.id,class_subject_id=cs.id,subject_session_id=lesson.id,start_at=start,end_at=start+timedelta(hours=2),room_id=7,teacher_user_id=teacher.id);db.add(row);db.commit()
 finally: db.close()
 payload={'start_at':start.isoformat(),'end_at':(start+timedelta(hours=1)).isoformat(),'room_id':7,'teacher_user_id':teacher.id}
 r=client.post('/api/s4/conflicts/check',headers=admin_headers,json=payload);assert r.status_code==200;rj=r.json();assert rj['has_conflict'];reasons=' '.join(rj['conflicts'][0]['reasons']);assert 'Phòng' in reasons and 'Giảng viên' in reasons
