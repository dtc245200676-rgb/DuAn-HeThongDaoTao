from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.sprint3 import ClassEnrollment, StudentProfile
from app.models.training import TrainingClass, TrainingProgram
from app.models.user import User


def test_bulk_enrollment_capacity_and_duplicate(client, user_factory, admin_headers):
    u1=user_factory("s61@example.com","Pass1234","student",full_name="SV 61")
    u2=user_factory("s62@example.com","Pass1234","student",full_name="SV 62")
    u3=user_factory("s63@example.com","Pass1234","student",full_name="SV 63")
    db=SessionLocal()
    try:
        p=TrainingProgram(code="P06",name="Program 06",total_duration_hours=1,standard_tuition=0,status="active")
        db.add(p);db.flush()
        c=TrainingClass(program_id=p.id,name="C06",code="C06",status="preparing",max_students=2,delivery_mode="offline")
        db.add(c);db.flush()
        profiles=[]
        for idx,u in enumerate([u1,u2,u3],start=1):
            sp=StudentProfile(student_code=f"HV06{idx}",user_id=u.id);db.add(sp);db.flush();profiles.append(sp.id)
        db.commit();cid=c.id
    finally: db.close()

    r=client.post(f"/api/s3/enrollments/classes/{cid}",headers=admin_headers,json={"student_ids":profiles[:2]})
    assert r.status_code==200, r.text
    assert r.json()["current_students"]==2
    dup=client.post(f"/api/s3/enrollments/classes/{cid}",headers=admin_headers,json={"student_ids":[profiles[0]]})
    assert dup.status_code==409
    full=client.post(f"/api/s3/enrollments/classes/{cid}",headers=admin_headers,json={"student_ids":[profiles[2]]})
    assert full.status_code==409
    db=SessionLocal()
    try:
        rows=db.scalars(select(ClassEnrollment).where(ClassEnrollment.class_id==cid)).all()
        assert len(rows)==2
        assert all(x.enrolled_by_user_id is not None for x in rows)
    finally: db.close()
