from datetime import datetime
from t1_construcao.domain import AppointmentRepository, ServiceRepository
from t1_construcao.application.dtos import UpdateAppointmentDto, AppointmentResponseDto
from .assemblers.appointment_assembler import to_appointment_dto
from fastapi import HTTPException

__all__ = ["UpdateAppointmentUsecase"]


class UpdateAppointmentUsecase:

    def __init__(
        self,
        appointment_id: str,
        update_appointment_dto: UpdateAppointmentDto,
        appointment_repository: AppointmentRepository,
        service_repository: ServiceRepository,
    ):
        self._appointment_id = appointment_id
        self._update_appointment_dto = update_appointment_dto
        self._appointment_repository = appointment_repository
        self._service_repository = service_repository

    async def execute(self) -> AppointmentResponseDto:
        appointment = await self._appointment_repository.get_by_id(self._appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if appointment.status in ["cancelled", "completed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update appointment with status '{appointment.status}'",
            )

        # If updating scheduled_at, check for conflicts
        if self._update_appointment_dto.scheduled_at:
            if self._update_appointment_dto.scheduled_at <= datetime.now():
                raise HTTPException(
                    status_code=400,
                    detail="Appointment must be scheduled in the future",
                )

            service = await self._service_repository.get_by_id(appointment.service_id)
            if service:
                has_conflict = await self._appointment_repository.check_conflict(
                    service_id=appointment.service_id,
                    scheduled_at=self._update_appointment_dto.scheduled_at,
                    duration_minutes=service.duration_minutes,
                    exclude_appointment_id=self._appointment_id,
                )

                if has_conflict:
                    raise HTTPException(
                        status_code=409,
                        detail="There is a scheduling conflict for this time slot",
                    )

        appointment_entity = await self._appointment_repository.update(
            appointment_id=self._appointment_id,
            scheduled_at=self._update_appointment_dto.scheduled_at,
            notes=self._update_appointment_dto.notes,
        )
        return to_appointment_dto(appointment_entity)
