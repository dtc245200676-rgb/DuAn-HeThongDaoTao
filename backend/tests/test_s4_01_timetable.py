from datetime import date, time, timedelta
from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.sprint3 import ClassSubject
from app.models.sprint4 import AcademicHoliday, ClassScheduleSession
from app.models.training import ProgramSubject, Subject, SubjectSession, TrainingClass, TrainingProgram


def test_preview_skips_holiday_and_confirm_links_lessons(client,admin_headers):
    db=SessionLocal()
    try:
        p=TrainingProgram(code="P401",name="P401",total_duration_hours=10,standard_tuition=0,status="active")
        s=Subject(code="S401",name="S401",session_count=2,weight=100)
        db.add_all([p,s]);db.flush();db.add(ProgramSubject(program_id=p.id,subject_id=s.id,order_index=1));db.add_all([SubjectSession(subject_id=s.id,sequence=1,topic="Bài 1"),SubjectSession(subject_id=s.id,sequence=2,topic="Bài 2")]);db.flush()
        c=TrainingClass(program_id=p.id,name="C401",code="C401",expected_start_date=date.today(),max_students=20,delivery_mode="offline",status="preparing")
        db.add(c);db.flush();db.add(ClassSubject(class_id=c.id,subject_id=s.id,order_index=1));
        start=date.today()+timedelta(days=1);db.add(AcademicHoliday(holiday_date=start,name="Ngày nghỉ"));db.commit();cid=c.id
    finally: db.close()
    payload={"class_id":cid,"start_date":start.isoformat(),"weekdays":[0,1,2,3,4,5,6],"start_time":"08:00:00","duration_minutes":90}
    r=client.post('/api/s4/timetable/preview',headers=admin_headers,json=payload);assert r.status_code==200,r.text
    assert r.json()['count']==2 and not r.json()['sessions'][0]['start_at'].startswith(start.isoformat())
    r=client.post('/api/s4/timetable/confirm',headers=admin_headers,json=payload);assert r.status_code==200,r.text
    db=SessionLocal()
    try:
        rows=db.scalars(select(ClassScheduleSession).where(ClassScheduleSession.class_id==cid)).all();assert len(rows)==2;assert all(x.subject_session_id for x in rows)
    finally: db.close()
