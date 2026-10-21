from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

LEAD_FUNNEL_STATUSES = ["new", "contacted", "consulting", "trial", "closed", "rejected"]
CLASS_STATUSES = ["preparing", "studying", "completed", "cancelled"]


class LeadStatusMove(BaseModel):
    status: Literal["new", "contacted", "consulting", "trial", "closed", "rejected"]
    rejection_reason: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def rejection_requires_reason(self):
        if self.status == "rejected" and not (self.rejection_reason or "").strip():
            raise ValueError("Chuyển sang Từ chối bắt buộc phải chọn hoặc nhập lý do.")
        return self


class LeadInteractionCreate(BaseModel):
    interaction_type: Literal["call", "message", "meeting"]
    content: str = Field(min_length=1, max_length=5000)
    occurred_at: Optional[datetime] = None
    reminder_at: Optional[datetime] = None

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nội dung chăm sóc không được để trống.")
        return value


class ConvertLeadRequest(BaseModel):
    entry_level: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    date_of_birth: Optional[date] = None
    address: Optional[str] = Field(default=None, max_length=500)
    entry_level: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None


class TrainingClassCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    program_id: int
    expected_start_date: date
    max_students: int = Field(ge=1, le=1000)
    delivery_mode: Literal["offline", "online", "hybrid"] = "offline"


class TrainingClassUpdate(BaseModel):
    expected_start_date: Optional[date] = None
    max_students: Optional[int] = Field(default=None, ge=1, le=1000)
    delivery_mode: Optional[Literal["offline", "online", "hybrid"]] = None
    status: Optional[Literal["preparing", "studying", "completed", "cancelled"]] = None
    completed_sessions: Optional[int] = Field(default=None, ge=0)


class EnrollmentBulkCreate(BaseModel):
    student_ids: list[int] = Field(min_length=1)

    @field_validator("student_ids")
    @classmethod
    def unique_students(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Danh sách học viên không được trùng.")
        return value


class ClassStaffAssign(BaseModel):
    teacher_user_id: int
    assistant_user_ids: list[int] = []

    @field_validator("assistant_user_ids")
    @classmethod
    def unique_assistants(cls, value):
        return list(dict.fromkeys(value))


class RoomCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    room_type: Literal["physical", "online"]
    capacity: Optional[int] = Field(default=None, ge=1, le=10000)
    online_url: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_by_type(self):
        if self.room_type == "physical" and self.capacity is None:
            raise ValueError("Phòng vật lý phải khai báo sức chứa.")
        if self.room_type == "online" and not (self.online_url or "").strip():
            raise ValueError("Phòng trực tuyến phải có liên kết.")
        return self


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    capacity: Optional[int] = Field(default=None, ge=1, le=10000)
    online_url: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


class AssignRoomRequest(BaseModel):
    room_id: Optional[int] = None
