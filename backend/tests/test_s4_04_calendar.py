from datetime import date,datetime,timedelta
from app.db.database import SessionLocal
from app.models.sprint3 import ClassSubject
from app.models.sprint4 import ClassScheduleSession
from app.models.training import ProgramSubject,Subject,SubjectSession,TrainingClass,TrainingProgram

def test_calendar_week_filter_by_class(client,admin_headers):
 db=SessionLocal()
 try:
  p=TrainingProgram(code='P404',name='P',total_duration_hours=1,standard_tuition=0,status='active');s=Subject(code='S404',name='S',session_count=1,weight=100);db.add_all([p,s]);db.flush();db.add(ProgramSubject(program_id=p.id,subject_id=s.id,order_index=1));l=SubjectSession(subject_id=s.id,sequence=1,topic='B');db.add(l);c=TrainingClass(program_id=p.id,name='C404',code='C404',expected_start_date=date.today(),max_students=10,delivery_mode='offline',status='studying');db.add(c);db.flush();cs=ClassSubject(class_id=c.id,subject_id=s.id,order_index=1);db.add(cs);db.flush();start=datetime.now()+timedelta(days=2);db.add(ClassScheduleSession(class_id=c.id,class_subject_id=cs.id,subject_session_id=l.id,start_at=start,end_at=start+timedelta(hours=1)));db.commit();cid=c.id;anchor=start.date().isoformat()
 finally: db.close()
 r=client.get(f'/api/s4/calendar/events?view=week&anchor_date={anchor}&class_id={cid}',headers=admin_headers);assert r.status_code==200,r.text;assert len(r.json()['events'])==1;assert r.json()['events'][0]['class_code']=='C404'
