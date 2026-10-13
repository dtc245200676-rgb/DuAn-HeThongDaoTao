from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False, index=True)
    phone = Column(String(30), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    source = Column(String(100), nullable=True, index=True)
    interested_program_id = Column(Integer, ForeignKey("training_programs.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), nullable=False, default="new", index=True)
    assignee_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    interested_program = relationship("TrainingProgram")
    assignee = relationship("User", foreign_keys=[assignee_user_id])
    assignments = relationship("LeadAssignmentHistory", back_populates="lead", cascade="all, delete-orphan")


class LeadAssignmentHistory(Base):
    __tablename__ = "lead_assignment_history"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="assignments")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    actor_user = relationship("User", foreign_keys=[actor_user_id])
