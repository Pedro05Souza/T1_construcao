from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from src.t1_construcao.domain.entities.appointment_entity import AppointmentEntity


__all__ = ["AppointmentRepository"]


@runtime_checkable
class AppointmentRepository(Protocol):
    async def create(
        self,
        user_id: str,
        service_id: str,
        scheduled_at: datetime,
        notes: str | None = None,
    ) -> "AppointmentEntity":
        """Create a new appointment."""
        ...

    async def update(
        self,
        appointment_id: str,
        scheduled_at: datetime | None = None,
        notes: str | None = None,
        status: str | None = None,
    ) -> "AppointmentEntity":
        """Update an existing appointment."""
        ...

    async def get_by_id(self, appointment_id: str) -> "AppointmentEntity | None":
        """Retrieve an appointment by its ID."""
        ...

    async def delete(self, appointment_id: str) -> None:
        """Delete an appointment by its ID."""
        ...

    async def get_all(
        self,
        user_id: str | None = None,
        service_id: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list["AppointmentEntity"], int]:
        """Retrieve all appointments with pagination and filters. Returns (appointments, total_count)."""
        ...

    async def check_conflict(
        self,
        service_id: str,
        scheduled_at: datetime,
        duration_minutes: int,
        exclude_appointment_id: str | None = None,
    ) -> bool:
        """Check if there's a scheduling conflict. Returns True if conflict exists."""
        ...
