from datetime import datetime, timedelta

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.training import TrainingClass, TrainingProgram
from app.models.sprint3 import ClassEnrollment, StudentProfile


def create_demo_class():
    db = SessionLocal()
    try:
        program = TrainingProgram(code="S5TEST", name="Sprint 5 Test Program", total_duration_hours=10, standard_tuition=0, status="active")
        db.add(program)
        db.flush()
        item = TrainingClass(program_id=program.id, name="S5 Test Class", code="S5-TEST", status="studying", max_students=20, delivery_mode="offline")
        db.add(item)
        db.commit()
        db.refresh(item)
        return item.id
    finally:
        db.close()


def test_s5_class_options_and_warning_summary(client, admin_headers):
    class_id = create_demo_class()
    response = client.get("/api/s5/classes", headers=admin_headers)
    assert response.status_code == 200
    assert any(row["id"] == class_id for row in response.json())

    warnings = client.get("/api/s5/attendance/warnings?threshold=20", headers=admin_headers)
    assert warnings.status_code == 200
    assert warnings.json()["threshold"] == 20
    assert "items" in warnings.json()

    matrix = client.get(f"/api/s5/attendance/classes/{class_id}/matrix", headers=admin_headers)
    assert matrix.status_code == 200, matrix.text
    assert matrix.json()["class_id"] == class_id
    exported = client.get(f"/api/s5/attendance/classes/{class_id}/export", headers=admin_headers)
    assert exported.status_code == 200, exported.text
    assert "spreadsheetml" in exported.headers.get("content-type", "")


def test_s5_create_and_list_assignment(client, admin_headers):
    class_id = create_demo_class()
    due = (datetime.now() + timedelta(days=3)).replace(microsecond=0).isoformat()
    response = client.post(
        "/api/s5/assignments",
        headers=admin_headers,
        data={
            "title": "S5 test assignment",
            "description": "Assignment integration test",
            "class_ids": f"[{class_id}]",
            "due_at": due,
            "max_score": "10",
            "allow_late": "false",
            "publish": "true",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["title"] == "S5 test assignment"
    assert payload["status"] == "published"
    assert payload["classes"][0]["id"] == class_id

    listing = client.get("/api/s5/assignments", headers=admin_headers)
    assert listing.status_code == 200
    assert any(row["id"] == payload["id"] for row in listing.json())


def test_s5_student_can_submit_and_teacher_can_grade(client, admin_headers, user_factory):
    class_id = create_demo_class()
    student_user = user_factory("s5student@example.com", "Student1234", "student", full_name="Sprint Five Student")
    db = SessionLocal()
    try:
        student_profile = StudentProfile(student_code="S5-STUDENT-01", user_id=student_user.id, entry_level="basic")
        db.add(student_profile); db.flush()
        db.add(ClassEnrollment(class_id=class_id, student_id=student_profile.id, status="active"))
        db.commit()
        student_id = student_profile.id
    finally:
        db.close()

    due = (datetime.now() + timedelta(days=3)).replace(microsecond=0).isoformat()
    created = client.post("/api/s5/assignments", headers=admin_headers, data={
        "title": "S5 submission test", "description": "test upload", "class_ids": f"[{class_id}]",
        "due_at": due, "max_score": "10", "allow_late": "false", "publish": "true",
    })
    assert created.status_code == 200, created.text
    assignment_id = created.json()["id"]

    login = client.post("/api/auth/login", json={"email": "s5student@example.com", "password": "Student1234"})
    assert login.status_code == 200, login.text
    student_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    submitted = client.post(f"/api/s5/assignments/{assignment_id}/submissions", headers=student_headers,
                            data={"comment": "First version"}, files={"files": ("answer.txt", b"hello sprint 5", "text/plain")})
    assert submitted.status_code == 200, submitted.text
    submission = submitted.json()["submission"]
    assert submission["version"] == 1
    assert submission["files"][0]["name"] == "answer.txt"

    graded = client.patch(f"/api/s5/submissions/{submission['id']}/grade", headers=admin_headers,
                          json={"score": 8, "feedback": "Good", "status": "graded"})
    assert graded.status_code == 200, graded.text
    assert graded.json()["submission"]["score"] == 8.0
