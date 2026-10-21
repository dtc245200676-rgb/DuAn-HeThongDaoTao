from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class AcademicHoliday(Base):
    __tablename__ = "academic_holidays"

    id = Column(Integer, primary_key=True)
    holiday_date = Column(Date, nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_by = relationship("User")


class ClassScheduleSession(Base):
    __tablename__ = "class_schedule_sessions"
    __table_args__ = (UniqueConstraint("class_id", "subject_session_id", name="uq_class_schedule_lesson"),)

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("training_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    class_subject_id = Column(Integer, ForeignKey("class_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_session_id = Column(Integer, ForeignKey("subject_sessions.id", ondelete="RESTRICT"), nullable=False, index=True)
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("training_rooms.id", ondelete="SET NULL"), nullable=True, index=True)
    teacher_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="scheduled", index=True)  # scheduled|cancelled|completed
    cancellation_reason = Column(String(500), nullable=True)
    conflict_override = Column(Boolean, nullable=False, default=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    training_class = relationship("TrainingClass", foreign_keys=[class_id])
    class_subject = relationship("ClassSubject")
    subject_session = relationship("SubjectSession")
    room = relationship("TrainingRoom")
    teacher = relationship("User", foreign_keys=[teacher_user_id])
    created_by = relationship("User", foreign_keys=[created_by_user_id])


class ScheduleChangeHistory(Base):
    __tablename__ = "schedule_change_history"

    id = Column(Integer, primary_key=True)
    schedule_session_id = Column(Integer, ForeignKey("class_schedule_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(30), nullable=False)  # created|rescheduled|cancelled|override
    old_start_at = Column(DateTime, nullable=True)
    old_end_at = Column(DateTime, nullable=True)
    old_room_id = Column(Integer, nullable=True)
    old_teacher_user_id = Column(Integer, nullable=True)
    reason = Column(String(500), nullable=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    schedule_session = relationship("ClassScheduleSession")
    actor = relationship("User")


class UserNotification(Base):
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = relationship("User")


class StudentStatusHistory(Base):
    __tablename__ = "student_status_history"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(30), nullable=False, index=True)  # reserve|transfer|withdraw|reactivate
    from_class_id = Column(Integer, ForeignKey("training_classes.id", ondelete="SET NULL"), nullable=True)
    to_class_id = Column(Integer, ForeignKey("training_classes.id", ondelete="SET NULL"), nullable=True)
    effective_date = Column(Date, nullable=False, index=True)
    reason = Column(String(500), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    student = relationship("StudentProfile")
    actor = relationship("User")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("schedule_session_id", "student_id", name="uq_attendance_session_student"),)

    id = Column(Integer, primary_key=True)
    schedule_session_id = Column(Integer, ForeignKey("class_schedule_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), nullable=False, index=True)  # present|late|excused_absence|unexcused_absence
    note = Column(String(500), nullable=True)
    marked_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    marked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    schedule_session = relationship("ClassScheduleSession")
    student = relationship("StudentProfile")
    marked_by = relationship("User", foreign_keys=[marked_by_user_id])
    updated_by = relationship("User", foreign_keys=[updated_by_user_id])


class AttendanceAuditLog(Base):
    __tablename__ = "attendance_audit_logs"

    id = Column(Integer, primary_key=True)
    attendance_id = Column(Integer, ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)
    reason = Column(String(500), nullable=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    attendance = relationship("AttendanceRecord")
    actor = relationship("User")


class AbsenceRequest(Base):
    __tablename__ = "absence_requests"

    id = Column(Integer, primary_key=True)
    schedule_session_id = Column(Integer, ForeignKey("class_schedule_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    evidence_path = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending|approved|rejected
    reviewer_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    schedule_session = relationship("ClassScheduleSession")
    student = relationship("StudentProfile")
    reviewer = relationship("User")
