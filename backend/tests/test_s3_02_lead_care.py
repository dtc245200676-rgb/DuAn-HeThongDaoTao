from datetime import timedelta
from sqlalchemy import select

from app.core.security import utcnow
from app.db.database import SessionLocal
from app.models.lead import Lead
from app.models.user import User


def test_care_log_and_overdue_reminder(client, user_factory):
    user_factory("care@example.com", "Pass1234", "admissions", full_name="TVTS Care")
    token = client.post("/api/auth/login", json={"email": "care@example.com", "password": "Pass1234"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == "care@example.com"))
        lead = Lead(full_name="Khách B", phone="0902222222", status="contacted", assignee_user_id=user.id)
        db.add(lead); db.commit(); db.refresh(lead); lead_id = lead.id
    finally: db.close()

    r = client.post(f"/api/s3/care/leads/{lead_id}/interactions", headers=headers, json={
        "interaction_type": "call",
        "content": "Khách hẹn gọi lại",
        "reminder_at": (utcnow() - timedelta(hours=1)).isoformat(),
    })
    assert r.status_code == 200
    interaction_id = r.json()["id"]
    assert r.json()["is_overdue"] is True

    overdue = client.get("/api/s3/care/reminders?overdue_only=true", headers=headers)
    assert overdue.status_code == 200
    assert len(overdue.json()) == 1
    assert overdue.json()[0]["lead_name"] == "Khách B"

    done = client.patch(f"/api/s3/care/interactions/{interaction_id}/complete-reminder", headers=headers)
    assert done.status_code == 200
    assert client.get("/api/s3/care/reminders?overdue_only=true", headers=headers).json() == []
