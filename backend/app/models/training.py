from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class TrainingProgram(Base):
    __tablename__ = "training_programs"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_duration_hours = Column(Integer, nullable=False, default=0)
    standard_tuition = Column(Numeric(14, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    subjects = relationship("ProgramSubject", back_populates="program", cascade="all, delete-orphan")
    classes = relationship("TrainingClass", back_populates="program", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    session_count = Column(Integer, nullable=False, default=1)
    weight = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    learning_outcomes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    programs = relationship("ProgramSubject", back_populates="subject", cascade="all, delete-orphan", foreign_keys="ProgramSubject.subject_id")
    sessions = relationship("SubjectSession", back_populates="subject", cascade="all, delete-orphan", order_by="SubjectSession.sequence")


class ProgramSubject(Base):
    __tablename__ = "program_subjects"
    __table_args__ = (
        UniqueConstraint("program_id", "subject_id", name="uq_program_subject"),
        UniqueConstraint("program_id", "order_index", name="uq_program_subject_order"),
    )

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("training_programs.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    prerequisite_subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)

    program = relationship("TrainingProgram", back_populates="subjects")
    subject = relationship("Subject", back_populates="programs", foreign_keys=[subject_id])
    prerequisite_subject = relationship("Subject", foreign_keys=[prerequisite_subject_id])


class SubjectSession(Base):
    __tablename__ = "subject_sessions"
    __table_args__ = (UniqueConstraint("subject_id", "sequence", name="uq_subject_session_sequence"),)

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    topic = Column(String(255), nullable=False)
    objective = Column(Text, nullable=True)

    subject = relationship("Subject", back_populates="sessions")


class TrainingClass(Base):
    __tablename__ = "training_classes"

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("training_programs.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    status = Column(String(20), nullable=False, default="planned", index=True)

    program = relationship("TrainingProgram", back_populates="classes")
