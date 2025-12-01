from datetime import datetime, timedelta
from t1_construcao.domain import AppointmentEntity, AppointmentRepository
from ._repository_meta import RepositoryMeta
from ..models import Appointment, Service
from .mappers import appointment_model_to_entity

__all__ = ["AppointmentRepository"]


class AppointmentRepository(metaclass=RepositoryMeta):

    async def create(
        self,
        user_id: str,
        service_id: str,
        scheduled_at: datetime,
        notes: str | None = None,
    ) -> AppointmentEntity:
        appointment = await Appointment.create(
            user_id=user_id,
            service_id=service_id,
            scheduled_at=scheduled_at,
            notes=notes,
            status="pending",
        )
        return appointment_model_to_entity(appointment)

    async def update(
        self,
        appointment_id: str,
        scheduled_at: datetime | None = None,
        notes: str | None = None,
        status: str | None = None,
    ) -> AppointmentEntity:
        update_data = {}
        if scheduled_at is not None:
            update_data["scheduled_at"] = scheduled_at
        if notes is not None:
            update_data["notes"] = notes
        if status is not None:
            update_data["status"] = status

        if update_data:
            updated = await Appointment.filter(id=appointment_id).update(**update_data)
            if not updated:
                raise ValueError("Appointment not found")

        appointment_entity = await self.get_by_id(appointment_id)
        if appointment_entity is None:
            raise ValueError("Appointment not found")
        return appointment_entity

    async def get_by_id(self, appointment_id: str) -> AppointmentEntity | None:
        appointment = await Appointment.get(id=appointment_id)
        return appointment_model_to_entity(appointment) if appointment else None

    async def delete(self, appointment_id: str) -> None:
        deleted = await Appointment.filter(id=appointment_id).delete()
        if not deleted:
            raise ValueError("Appointment not found")
        return None

    async def get_all(
        self,
        user_id: str | None = None,
        service_id: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[AppointmentEntity], int]:
        query = Appointment.all()

        if user_id is not None:
            query = query.filter(user_id=user_id)
        if service_id is not None:
            query = query.filter(service_id=service_id)
        if status is not None:
            query = query.filter(status=status)
        if start_date is not None:
            query = query.filter(scheduled_at__gte=start_date)
        if end_date is not None:
            query = query.filter(scheduled_at__lte=end_date)

        total_count = await query.count()

        offset = (page - 1) * page_size
        appointments = (
            await query.offset(offset).limit(page_size).order_by("scheduled_at")
        )

        return [appointment_model_to_entity(apt) for apt in appointments], total_count

    async def check_conflict(
        self,
        service_id: str,
        scheduled_at: datetime,
        duration_minutes: int,
        exclude_appointment_id: str | None = None,
    ) -> bool:
        """Check if there's a scheduling conflict."""
        service = await Service.get(id=service_id)
        if not service:
            return False

        # Use service duration if not provided
        if duration_minutes <= 0:
            duration_minutes = service.duration_minutes

        start_time = scheduled_at
        end_time = scheduled_at + timedelta(minutes=duration_minutes)

        # Get all appointments for this service that might conflict
        # We check appointments that start within a reasonable window
        query = Appointment.filter(
            service_id=service_id,
            status__in=["pending", "confirmed"],
        )

        # Filter to appointments that might overlap (within 4 hours window for safety)
        window_start = start_time - timedelta(hours=2)
        window_end = end_time + timedelta(hours=2)

        conflicting_appointments = await query.filter(
            scheduled_at__gte=window_start,
            scheduled_at__lte=window_end,
        )

        if exclude_appointment_id:
            conflicting_appointments = [
                apt
                for apt in conflicting_appointments
                if str(apt.id) != exclude_appointment_id
            ]

        # For each potentially conflicting appointment, check actual overlap
        for apt in conflicting_appointments:
            apt_service = await Service.get(id=apt.service_id)
            if apt_service:
                apt_start = apt.scheduled_at
                apt_end = apt_start + timedelta(minutes=apt_service.duration_minutes)

                # Check if there's actual overlap
                # Overlap occurs if: apt_start < end_time AND apt_end > start_time
                if apt_start < end_time and apt_end > start_time:
                    return True

        return False
