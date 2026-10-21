from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime, nullable=False, index=True)
    max_score = Column(Numeric(8, 2), nullable=False, default=10)
    allow_late = Column(Boolean, nullable=False, default=False)
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft|published|archived
    attachment_files = Column(Text, nullable=True)  # JSON array: [{name,path,size}]
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = relationship("User")
    targets = relationship("AssignmentClass", cascade="all, delete-orphan", back_populates="assignment")
    extensions = relationship("AssignmentExtension", cascade="all, delete-orphan", back_populates="assignment")
    submissions = relationship("AssignmentSubmission", cascade="all, delete-orphan", back_populates="assignment")


class AssignmentClass(Base):
    __tablename__ = "assignment_classes"
    __table_args__ = (UniqueConstraint("assignment_id", "class_id", name="uq_assignment_class"),)

    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("training_classes.id", ondelete="CASCADE"), nullable=False, index=True)

    assignment = relationship("Assignment", back_populates="targets")
    training_class = relationship("TrainingClass")


class AssignmentExtension(Base):
    __tablename__ = "assignment_extensions"
    __table_args__ = (UniqueConstraint("assignment_id", "student_id", name="uq_assignment_extension_student"),)

    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    extended_due_at = Column(DateTime, nullable=False)
    reason = Column(String(500), nullable=False)
    granted_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    assignment = relationship("Assignment", back_populates="extensions")
    student = relationship("StudentProfile")
    granted_by = relationship("User")


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (UniqueConstraint("assignment_id", "student_id", "version", name="uq_assignment_submission_version"),)

    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    file_items = Column(Text, nullable=False)  # JSON array of uploaded file metadata
    comment = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="submitted", index=True)  # submitted|graded|needs_revision
    is_late = Column(Boolean, nullable=False, default=False, index=True)
    score = Column(Numeric(8, 2), nullable=True)
    feedback = Column(Text, nullable=True)
    graded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("StudentProfile")
    graded_by = relationship("User")
