from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    date_of_birth: Optional[date] = None
    address: Optional[str] = Field(default=None, max_length=500)

    @field_validator("phone")
    @classmethod
    def validate_vn_phone(cls, value):
        if value in (None, ""):
            return None
        digits = "".join(ch for ch in value if ch.isdigit())
        if value.startswith("+84"):
            digits = "0" + digits[2:]
        if len(digits) != 10 or not digits.startswith(("03", "05", "07", "08", "09")):
            raise ValueError("Số điện thoại Việt Nam không hợp lệ.")
        return digits


class TrainingProgramCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    total_duration_hours: int = Field(default=0, ge=0)
    standard_tuition: Decimal = Field(default=0, ge=0)
    status: str = "active"


class TrainingProgramUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    total_duration_hours: Optional[int] = Field(default=None, ge=0)
    standard_tuition: Optional[Decimal] = Field(default=None, ge=0)
    status: Optional[str] = None


class SubjectCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    session_count: int = Field(default=1, ge=1, le=500)
    weight: int = Field(default=0, ge=0, le=100)
    description: Optional[str] = None
    learning_outcomes: Optional[str] = None


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    session_count: Optional[int] = Field(default=None, ge=1, le=500)
    weight: Optional[int] = Field(default=None, ge=0, le=100)
    description: Optional[str] = None
    learning_outcomes: Optional[str] = None


class ProgramSubjectAdd(BaseModel):
    subject_id: int
    prerequisite_subject_id: Optional[int] = None


class ProgramSubjectReorder(BaseModel):
    subject_ids: list[int]


class ProgramSubjectPrerequisite(BaseModel):
    prerequisite_subject_id: Optional[int] = None


class SubjectSessionCreate(BaseModel):
    sequence: int = Field(ge=1)
    topic: str = Field(min_length=1, max_length=255)
    objective: Optional[str] = None


class CloneSessionsRequest(BaseModel):
    source_subject_id: int


class PublicLeadCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=9, max_length=30)
    email: Optional[EmailStr] = None
    source: Optional[str] = Field(default="website", max_length=100)
    interested_program_id: Optional[int] = None
    website: Optional[str] = None


class LeadCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=9, max_length=30)
    email: Optional[EmailStr] = None
    source: Optional[str] = Field(default=None, max_length=100)
    interested_program_id: Optional[int] = None
    status: str = "new"
    note: Optional[str] = None


class LeadUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    phone: Optional[str] = Field(default=None, min_length=9, max_length=30)
    email: Optional[EmailStr] = None
    source: Optional[str] = Field(default=None, max_length=100)
    interested_program_id: Optional[int] = None
    status: Optional[str] = None
    note: Optional[str] = None


class LeadAssignRequest(BaseModel):
    lead_ids: list[int] = Field(min_length=1)
    assignee_user_id: int
