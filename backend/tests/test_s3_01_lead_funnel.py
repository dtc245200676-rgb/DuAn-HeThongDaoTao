from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.lead import Lead
from app.models.sprint3 import LeadStatusHistory


def test_funnel_move_and_rejection_reason(client, user_factory):
    user_factory("admission1@example.com", "Pass1234", "admissions", full_name="TVTS 1")
    login = client.post("/api/auth/login", json={"email": "admission1@example.com", "password": "Pass1234"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    db = SessionLocal()
    try:
        from app.models.user import User
        user = db.scalar(select(User).where(User.email == "admission1@example.com"))
        lead = Lead(full_name="Khách A", phone="0901111111", status="new", assignee_user_id=user.id)
        db.add(lead); db.commit(); db.refresh(lead); lead_id = lead.id
    finally:
        db.close()

    funnel = client.get("/api/s3/funnel", headers=headers)
    assert funnel.status_code == 200
    new_col = next(x for x in funnel.json()["columns"] if x["status"] == "new")
    assert new_col["count"] == 1

    moved = client.patch(f"/api/s3/funnel/leads/{lead_id}/status", json={"status": "contacted"}, headers=headers)
    assert moved.status_code == 200
    assert moved.json()["status"] == "contacted"

    invalid = client.patch(f"/api/s3/funnel/leads/{lead_id}/status", json={"status": "rejected"}, headers=headers)
    assert invalid.status_code == 422

    rejected = client.patch(f"/api/s3/funnel/leads/{lead_id}/status", json={"status": "rejected", "rejection_reason": "Không còn nhu cầu"}, headers=headers)
    assert rejected.status_code == 200

    db = SessionLocal()
    try:
        history = db.scalars(select(LeadStatusHistory).where(LeadStatusHistory.lead_id == lead_id)).all()
        assert len(history) == 2
        assert history[-1].reason == "Không còn nhu cầu"
    finally:
        db.close()
