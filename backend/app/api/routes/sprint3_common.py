from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.routes.lead_common import admissions_only
from app.models.sprint3 import ClassEnrollment, ClassSubject, ClassSubjectStaff, StudentProfile, TrainingRoom
from app.models.training import Subject, TrainingClass


def ensure_lead_access(lead, context):
    if admissions_only(context) and lead.assignee_user_id != context.user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Bạn chỉ được thao tác lead được phân công cho mình.")


def role_slugs(user) -> set[str]:
    return {role.slug for role in user.roles}


def active_enrollment_count(db: Session, class_id: int) -> int:
    return db.scalar(
        select(func.count(ClassEnrollment.id)).where(
            ClassEnrollment.class_id == class_id,
            ClassEnrollment.status == "active",
        )
    ) or 0


def class_total_sessions(db: Session, class_id: int) -> int:
    return db.scalar(
        select(func.coalesce(func.sum(Subject.session_count), 0))
        .select_from(ClassSubject)
        .join(Subject, Subject.id == ClassSubject.subject_id)
        .where(ClassSubject.class_id == class_id)
    ) or 0


def serialize_class(db: Session, item: TrainingClass) -> dict:
    current = active_enrollment_count(db, item.id)
    total_sessions = int(class_total_sessions(db, item.id))
    room = db.get(TrainingRoom, item.room_id) if item.room_id else None
    return {
        "id": item.id,
        "code": item.code or item.name,
        "name": item.name,
        "program_id": item.program_id,
        "program_name": item.program.name if item.program else None,
        "expected_start_date": item.expected_start_date,
        "max_students": item.max_students,
        "delivery_mode": item.delivery_mode,
        "status": item.status,
        "current_students": current,
        "completed_sessions": item.completed_sessions,
        "total_sessions": total_sessions,
        "room_id": item.room_id,
        "room_name": room.name if room else None,
        "room_type": room.room_type if room else None,
        "capacity_warning": bool(room and room.room_type == "physical" and room.capacity is not None and current > room.capacity),
        "created_at": item.created_at,
    }


def serialize_student(db: Session, student: StudentProfile) -> dict:
    user = student.user
    rows = db.execute(
        select(TrainingClass.code, TrainingClass.name, TrainingClass.status, ClassEnrollment.status)
        .join(ClassEnrollment, ClassEnrollment.class_id == TrainingClass.id)
        .where(ClassEnrollment.student_id == student.id)
        .order_by(TrainingClass.id.desc())
    ).all()
    current, history = [], []
    for code, name, class_status, enrollment_status in rows:
        label = code or name
        if enrollment_status == "active" and class_status in {"preparing", "studying", "planned", "running", "active"}:
            current.append(label)
        else:
            history.append(label)
    return {
        "id": student.id,
        "student_code": student.student_code,
        "user_id": student.user_id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": user.date_of_birth,
        "address": user.address,
        "entry_level": student.entry_level,
        "notes": student.notes,
        "source_lead_id": student.source_lead_id,
        "current_classes": current,
        "class_history": history,
    }
