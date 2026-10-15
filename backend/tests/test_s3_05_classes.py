from datetime import date
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.sprint3 import ClassSubject
from app.models.training import ProgramSubject, Subject, TrainingProgram


def test_open_class_copies_curriculum_and_code_unique(client, admin_headers):
    db=SessionLocal()
    try:
        p=TrainingProgram(code="P05",name="Fullstack 05",total_duration_hours=100,standard_tuition=0,status="active")
        a=Subject(code="S05A",name="HTML",session_count=2,weight=30)
        b=Subject(code="S05B",name="JS",session_count=3,weight=70)
        db.add_all([p,a,b]);db.flush()
        db.add_all([ProgramSubject(program_id=p.id,subject_id=a.id,order_index=1),ProgramSubject(program_id=p.id,subject_id=b.id,order_index=2,prerequisite_subject_id=a.id)])
        db.commit();pid=p.id
    finally: db.close()

    payload={"code":"CGK01","program_id":pid,"expected_start_date":date.today().isoformat(),"max_students":25,"delivery_mode":"offline"}
    r=client.post("/api/s3/classes-manage/classes",headers=admin_headers,json=payload)
    assert r.status_code==200, r.text
    assert r.json()["copied_subject_count"]==2
    class_id=r.json()["id"]
    db=SessionLocal()
    try:
        rows=db.scalars(select(ClassSubject).where(ClassSubject.class_id==class_id).order_by(ClassSubject.order_index)).all()
        assert len(rows)==2
        assert rows[1].prerequisite_subject_id==rows[0].subject_id
    finally: db.close()
    assert client.post("/api/s3/classes-manage/classes",headers=admin_headers,json=payload).status_code==409
    assert client.put(f"/api/s3/classes-manage/classes/{class_id}",headers=admin_headers,json={"status":"studying"}).status_code==200
    assert client.put(f"/api/s3/classes-manage/classes/{class_id}",headers=admin_headers,json={"status":"preparing"}).status_code==409
