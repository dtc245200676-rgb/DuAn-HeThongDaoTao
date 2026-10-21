from datetime import date, datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

AttendanceStatus = Literal["present", "late", "excused_absence", "unexcused_absence"]


class TimetableGenerateRequest(BaseModel):
    class_id: int
    start_date: date
    weekdays: list[int] = Field(min_length=1)
    start_time: time
    duration_minutes: int = Field(default=120, ge=15, le=480)
    room_id: Optional[int] = None
    teacher_user_id: Optional[int] = None
    force_override: bool = False

    @field_validator("weekdays")
    @classmethod
    def validate_weekdays(cls, value):
        value = list(dict.fromkeys(value))
        if any(x < 0 or x > 6 for x in value):
            raise ValueError("Thứ trong tuần phải từ 0 (Thứ Hai) đến 6 (Chủ nhật).")
        return sorted(value)


class HolidayCreate(BaseModel):
    holiday_date: date
    name: str = Field(min_length=1, max_length=200)


class HolidayUpdate(BaseModel):
    holiday_date: Optional[date] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)


class ConflictCheckRequest(BaseModel):
    start_at: datetime
    end_at: datetime
    room_id: Optional[int] = None
    teacher_user_id: Optional[int] = None
    exclude_session_id: Optional[int] = None

    @model_validator(mode="after")
    def check_range(self):
        if self.end_at <= self.start_at:
            raise ValueError("Giờ kết thúc phải sau giờ bắt đầu.")
        return self


class ScheduleSessionChange(BaseModel):
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    room_id: Optional[int] = None
    teacher_user_id: Optional[int] = None
    status: Optional[Literal["scheduled", "cancelled"]] = None
    reason: Optional[str] = Field(default=None, max_length=500)
    force_override: bool = False

    @model_validator(mode="after")
    def validate_cancel(self):
        if self.status == "cancelled" and not (self.reason or "").strip():
            raise ValueError("Hủy buổi bắt buộc nhập lý do.")
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValueError("Giờ kết thúc phải sau giờ bắt đầu.")
        return self


class StudentStatusAction(BaseModel):
    class_id: int
    effective_date: date
    reason: str = Field(min_length=1, max_length=500)


class StudentTransferAction(BaseModel):
    from_class_id: int
    to_class_id: int
    effective_date: date
    reason: str = Field(min_length=1, max_length=500)


class AttendanceItem(BaseModel):
    student_id: int
    status: AttendanceStatus
    note: Optional[str] = Field(default=None, max_length=500)


class AttendanceSaveRequest(BaseModel):
    items: list[AttendanceItem] = Field(min_length=1)
    correction_reason: Optional[str] = Field(default=None, max_length=500)


class AbsenceReviewRequest(BaseModel):
    status: Literal["approved", "rejected"]
    reason: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def reject_reason(self):
        if self.status == "rejected" and not (self.reason or "").strip():
            raise ValueError("Từ chối đơn phải ghi lý do.")
        return self
