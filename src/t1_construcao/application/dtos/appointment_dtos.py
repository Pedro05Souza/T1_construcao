from pydantic import BaseModel, Field
from datetime import datetime


__all__ = [
    "CreateAppointmentDto",
    "UpdateAppointmentDto",
    "AppointmentResponseDto",
    "AppointmentListFilterDto",
    "ConfirmAppointmentDto",
    "CancelAppointmentDto",
]


class CreateAppointmentDto(BaseModel):
    service_id: str
    scheduled_at: datetime = Field(..., description="Data e hora do agendamento")
    notes: str | None = None


class UpdateAppointmentDto(BaseModel):
    scheduled_at: datetime | None = None
    notes: str | None = None


class ConfirmAppointmentDto(BaseModel):
    pass


class CancelAppointmentDto(BaseModel):
    reason: str | None = None


class AppointmentResponseDto(BaseModel):
    id: str
    user_id: str
    service_id: str
    scheduled_at: datetime
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class AppointmentListFilterDto(BaseModel):
    user_id: str | None = None
    service_id: str | None = None
    status: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
