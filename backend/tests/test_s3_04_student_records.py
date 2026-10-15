from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.sprint3 import ClassEnrollment, StudentProfile
from app.models.training import TrainingClass, TrainingProgram
from app.models.user import User


def test_student_search_update_and_class_history(client, user_factory, admin_headers):
    student_user = user_factory("student4@example.com", "Pass1234", "student", full_name="Nguyễn Sinh Viên")
    db=SessionLocal()
    try:
        user=db.get(User,student_user.id)
        profile=StudentProfile(student_code="HV202600004",user_id=user.id,entry_level="Cơ bản")
        program=TrainingProgram(code="P04",name="Program 04",total_duration_hours=10,standard_tuition=0,status="active")
        db.add_all([profile,program]);db.flush()
        current=TrainingClass(program_id=program.id,name="L04-A",code="L04-A",status="studying",max_students=20,delivery_mode="offline")
        old=TrainingClass(program_id=program.id,name="L04-OLD",code="L04-OLD",status="completed",max_students=20,delivery_mode="offline")
        db.add_all([current,old]);db.flush()
        db.add_all([ClassEnrollment(class_id=current.id,student_id=profile.id,status="active"),ClassEnrollment(class_id=old.id,student_id=profile.id,status="active")])
        db.commit(); profile_id=profile.id
    finally: db.close()

    r=client.get("/api/s3/students?q=HV202600004",headers=admin_headers)
    assert r.status_code==200
    assert r.json()["total"]==1
    item=r.json()["items"][0]
    assert "L04-A" in item["current_classes"]
    assert "L04-OLD" in item["class_history"]

    updated=client.put(f"/api/s3/students/{profile_id}",headers=admin_headers,json={"full_name":"Nguyễn SV Mới","phone":"0904444444","entry_level":"Khá","notes":"Ghi chú mới"})
    assert updated.status_code==200
    assert updated.json()["full_name"]=="Nguyễn SV Mới"
    assert updated.json()["entry_level"]=="Khá"
