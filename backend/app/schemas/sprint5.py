from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class AssignmentUpdate(BaseModel):
    due_at: datetime | None = None
    allow_late: bool | None = None
    status: Literal["draft", "published", "archived"] | None = None


class AssignmentExtensionCreate(BaseModel):
    student_id: int
    extended_due_at: datetime
    reason: str = Field(min_length=1, max_length=500)


class AssignmentGrade(BaseModel):
    score: float | None = Field(default=None, ge=0)
    feedback: str = Field(default="", max_length=4000)
    status: Literal["graded", "needs_revision"] = "graded"

