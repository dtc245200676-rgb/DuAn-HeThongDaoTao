from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_current_context
from app.db.database import get_db
from app.models.sprint3 import ClassEnrollment, ClassSubjectStaff, StudentProfile
from app.models.sprint4 import (
    ClassScheduleSession, StudentStatusHistory, UserNotification,
)
from app.models.training import Subject, SubjectSession, TrainingClass
from app.models.user import User

router = APIRouter(prefix="/api/s4", tags=["Sprint 4 Shared"])


def notify(db: Session, user_id: int, title: str, message: str, link: str | None = None):
    db.add(UserNotification(user_id=user_id, title=title, message=message, link=link))


def session_conflicts(db: Session, start_at: datetime, end_at: datetime, room_id: int | None, teacher_user_id: int | None, exclude_session_id: int | None = None):
    stmt = select(ClassScheduleSession).where(
        ClassScheduleSession.status == "scheduled",
        ClassScheduleSession.start_at < end_at,
        ClassScheduleSession.end_at > start_at,
    )
    if exclude_session_id:
        stmt = stmt.where(ClassScheduleSession.id != exclude_session_id)
    rows = db.scalars(stmt).all()
    result = []
    for row in rows:
        reasons = []
        if room_id is not None and row.room_id == room_id:
            reasons.append("Phòng đã được xếp cho lớp khác trong cùng khung giờ.")
        if teacher_user_id is not None and row.teacher_user_id == teacher_user_id:
            reasons.append("Giảng viên đã được xếp dạy lớp khác trong cùng khung giờ.")
        if reasons:
            cl = db.get(TrainingClass, row.class_id)
            result.append({
                "session_id": row.id,
                "class_id": row.class_id,
                "class_code": cl.code if cl else str(row.class_id),
                "start_at": row.start_at.isoformat(),
                "end_at": row.end_at.isoformat(),
                "reasons": reasons,
            })
    return result


def primary_teacher_for_class_subject(db: Session, class_subject_id: int) -> int | None:
    row = db.scalar(select(ClassSubjectStaff).where(
        ClassSubjectStaff.class_subject_id == class_subject_id,
        ClassSubjectStaff.staff_role == "teacher",
    ))
    return row.user_id if row else None


def serialize_schedule(db: Session, item: ClassScheduleSession):
    cl = db.get(TrainingClass, item.class_id)
    lesson = db.get(SubjectSession, item.subject_session_id)
    subject = db.get(Subject, lesson.subject_id) if lesson else None
    teacher = db.get(User, item.teacher_user_id) if item.teacher_user_id else None
    return {
        "id": item.id,
        "class_id": item.class_id,
        "class_code": cl.code if cl else None,
        "class_subject_id": item.class_subject_id,
        "subject_session_id": item.subject_session_id,
        "subject_code": subject.code if subject else None,
        "subject_name": subject.name if subject else None,
        "lesson_sequence": lesson.sequence if lesson else None,
        "lesson_topic": lesson.topic if lesson else None,
        "start_at": item.start_at.isoformat(),
        "end_at": item.end_at.isoformat(),
        "room_id": item.room_id,
        "teacher_user_id": item.teacher_user_id,
        "teacher_name": teacher.full_name if teacher else None,
        "status": item.status,
        "cancellation_reason": item.cancellation_reason,
        "conflict_override": bool(item.conflict_override),
    }


def student_effective_state(db: Session, student_id: int, class_id: int, on_date: date):
    # Start from enrollment; then apply status events effective up to the session date.
    enrollment = db.scalar(select(ClassEnrollment).where(
        ClassEnrollment.student_id == student_id,
        ClassEnrollment.class_id == class_id,
    ))
    if not enrollment:
        return "not_enrolled"
    state = "active" if enrollment.status == "active" else enrollment.status
    if state == "pending_transfer":
        state = "not_active"
    events = db.scalars(select(StudentStatusHistory).where(
        StudentStatusHistory.student_id == student_id,
        StudentStatusHistory.effective_date <= on_date,
        or_(StudentStatusHistory.from_class_id == class_id, StudentStatusHistory.to_class_id == class_id),
    ).order_by(StudentStatusHistory.effective_date, StudentStatusHistory.id)).all()
    for ev in events:
        if ev.action == "reserve" and ev.from_class_id == class_id:
            state = "reserved"
        elif ev.action == "withdraw" and ev.from_class_id == class_id:
            state = "withdrawn"
        elif ev.action == "transfer" and ev.from_class_id == class_id:
            state = "transferred"
        elif ev.action == "transfer" and ev.to_class_id == class_id:
            state = "active"
        elif ev.action == "reactivate" and ev.to_class_id == class_id:
            state = "active"
    return state


def eligible_students_for_session(db: Session, schedule: ClassScheduleSession):
    rows = db.scalars(select(ClassEnrollment).where(
        ClassEnrollment.class_id == schedule.class_id,
        ClassEnrollment.status.in_(["active", "reserved", "transferred", "pending_transfer"]),
    )).all()
    result=[]
    d=schedule.start_at.date()
    for enr in rows:
        if student_effective_state(db, enr.student_id, schedule.class_id, d) == "active":
            student=db.get(StudentProfile,enr.student_id)
            if student: result.append(student)
    return result


def can_manage_past_attendance(context: AuthContext):
    return "system_admin" in context.role_slugs or "training_manager" in context.role_slugs or "academic_affairs" in context.role_slugs


@router.get("/notifications/me")
def my_notifications(context: AuthContext = Depends(get_current_context), db: Session = Depends(get_db)):
    rows = db.scalars(select(UserNotification).where(UserNotification.user_id == context.user.id).order_by(UserNotification.created_at.desc()).limit(50)).all()
    return [{
        "id": x.id, "title": x.title, "message": x.message, "link": x.link,
        "read_at": x.read_at.isoformat() if x.read_at else None,
        "created_at": x.created_at.isoformat(),
    } for x in rows]
