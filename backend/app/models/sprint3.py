from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class LeadStatusHistory(Base):
    __tablename__ = "lead_status_history"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    lead = relationship("Lead")
    actor = relationship("User")


class LeadInteraction(Base):
    __tablename__ = "lead_interactions"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    reminder_at = Column(DateTime, nullable=True, index=True)
    reminder_completed_at = Column(DateTime, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    lead = relationship("Lead")
    created_by = relationship("User")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)
    student_code = Column(String(30), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True, index=True)
    source_lead_id = Column(Integer, ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, unique=True)
    entry_level = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    source_lead = relationship("Lead")


class ClassSubject(Base):
    __tablename__ = "class_subjects"
    __table_args__ = (
        UniqueConstraint("class_id", "subject_id", name="uq_class_subject"),
        UniqueConstraint("class_id", "order_index", name="uq_class_subject_order"),
    )

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("training_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    prerequisite_subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)

    training_class = relationship("TrainingClass", foreign_keys=[class_id])
    subject = relationship("Subject", foreign_keys=[subject_id])
    prerequisite_subject = relationship("Subject", foreign_keys=[prerequisite_subject_id])


class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"
    __table_args__ = (UniqueConstraint("class_id", "student_id", name="uq_class_enrollment"),)

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("training_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    enrolled_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    enrolled_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    training_class = relationship("TrainingClass", foreign_keys=[class_id])
    student = relationship("StudentProfile")
    enrolled_by = relationship("User")


class ClassSubjectStaff(Base):
    __tablename__ = "class_subject_staff"
    __table_args__ = (UniqueConstraint("class_subject_id", "user_id", "staff_role", name="uq_class_subject_staff"),)

    id = Column(Integer, primary_key=True)
    class_subject_id = Column(Integer, ForeignKey("class_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    staff_role = Column(String(20), nullable=False, index=True)  # teacher | assistant
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    assigned_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    class_subject = relationship("ClassSubject")
    user = relationship("User", foreign_keys=[user_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_user_id])


class TrainingRoom(Base):
    __tablename__ = "training_rooms"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(150), nullable=False)
    room_type = Column(String(20), nullable=False, default="physical", index=True)  # physical | online
    capacity = Column(Integer, nullable=True)
    online_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
