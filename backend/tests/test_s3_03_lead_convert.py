from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.lead import Lead
from app.models.sprint3 import StudentProfile
from app.models.tokens import ActivationToken
from app.models.user import User


def test_convert_closed_lead_to_student(client, user_factory):
    user_factory("convert@example.com", "Pass1234", "admissions", full_name="TVTS Convert")
    token = client.post("/api/auth/login", json={"email":"convert@example.com","password":"Pass1234"}).json()["access_token"]
    headers={"Authorization":f"Bearer {token}"}
    db=SessionLocal()
    try:
        owner=db.scalar(select(User).where(User.email=="convert@example.com"))
        lead=Lead(full_name="Nguyễn Học Viên",phone="0903333333",email="student3@example.com",status="closed",assignee_user_id=owner.id)
        db.add(lead);db.commit();db.refresh(lead);lead_id=lead.id
    finally: db.close()

    r=client.post(f"/api/s3/convert/leads/{lead_id}/student",headers=headers,json={"entry_level":"Cơ bản","notes":"Đã tư vấn"})
    assert r.status_code==200, r.text
    assert r.json()["student_code"].startswith("HV")
    assert r.json()["debug_temporary_password"]

    db=SessionLocal()
    try:
        lead=db.get(Lead,lead_id)
        assert lead.status=="enrolled"
        student=db.scalar(select(StudentProfile).where(StudentProfile.source_lead_id==lead_id))
        assert student is not None
        user=db.get(User,student.user_id)
        assert user.email=="student3@example.com"
        assert "student" in {x.slug for x in user.roles}
        assert db.scalar(select(ActivationToken).where(ActivationToken.user_id==user.id)) is not None
    finally: db.close()

    locked=client.put(f"/api/leads/{lead_id}",headers=headers,json={"note":"không được sửa"})
    assert locked.status_code==409
