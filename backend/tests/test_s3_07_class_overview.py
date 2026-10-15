from datetime import date, timedelta

from app.db.database import SessionLocal
from app.models.sprint3 import ClassEnrollment, ClassSubject, StudentProfile
from app.models.training import Subject, TrainingClass, TrainingProgram


def test_class_overview_filters_and_quick_metrics(client, user_factory, admin_headers):
    student=user_factory("s7@example.com","Pass1234","student",full_name="SV7")
    db=SessionLocal()
    try:
        p=TrainingProgram(code="P07",name="Program 07",total_duration_hours=1,standard_tuition=0,status="active")
        s=Subject(code="SUB07",name="Môn 07",session_count=5,weight=100)
        db.add_all([p,s]);db.flush()
        c1=TrainingClass(program_id=p.id,name="C07A",code="C07A",status="studying",max_students=10,delivery_mode="offline",expected_start_date=date.today(),completed_sessions=2)
        c2=TrainingClass(program_id=p.id,name="C07B",code="C07B",status="preparing",max_students=15,delivery_mode="online",expected_start_date=date.today()+timedelta(days=5))
        db.add_all([c1,c2]);db.flush();db.add_all([ClassSubject(class_id=c1.id,subject_id=s.id,order_index=1),ClassSubject(class_id=c2.id,subject_id=s.id,order_index=1)])
        sp=StudentProfile(student_code="HV07",user_id=student.id);db.add(sp);db.flush();db.add(ClassEnrollment(class_id=c1.id,student_id=sp.id,status="active"));db.commit();pid=p.id
    finally: db.close()

    r=client.get(f"/api/s3/class-overview/classes?status=studying&program_id={pid}",headers=admin_headers)
    assert r.status_code==200
    assert r.json()["total"]==1
    item=r.json()["items"][0]
    assert item["current_students"]==1
    assert item["max_students"]==10
    assert item["completed_sessions"]==2
    assert item["total_sessions"]==5
    assert r.json()["quick"]["studying"]==1
