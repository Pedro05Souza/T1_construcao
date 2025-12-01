from datetime import datetime
from t1_construcao.domain import AppointmentRepository, ServiceRepository
from t1_construcao.application.dtos import CreateAppointmentDto, AppointmentResponseDto
from .assemblers.appointment_assembler import to_appointment_dto
from fastapi import HTTPException

__all__ = ["CreateAppointmentUsecase"]


class CreateAppointmentUsecase:

    def __init__(
        self,
        user_id: str,
        create_appointment_dto: CreateAppointmentDto,
        appointment_repository: AppointmentRepository,
        service_repository: ServiceRepository,
    ):
        self._user_id = user_id
        self._create_appointment_dto = create_appointment_dto
        self._appointment_repository = appointment_repository
        self._service_repository = service_repository

    async def execute(self) -> AppointmentResponseDto:
        # Validate service exists and is active
        service = await self._service_repository.get_by_id(
            self._create_appointment_dto.service_id
        )
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        if not service.is_active:
            raise HTTPException(status_code=400, detail="Service is not active")

        # Validate scheduled_at is in the future
        if self._create_appointment_dto.scheduled_at <= datetime.now():
            raise HTTPException(
                status_code=400, detail="Appointment must be scheduled in the future"
            )

        # Check for scheduling conflicts
        has_conflict = await self._appointment_repository.check_conflict(
            service_id=self._create_appointment_dto.service_id,
            scheduled_at=self._create_appointment_dto.scheduled_at,
            duration_minutes=service.duration_minutes,
        )

        if has_conflict:
            raise HTTPException(
                status_code=409,
                detail="There is a scheduling conflict for this time slot",
            )

        appointment_entity = await self._appointment_repository.create(
            user_id=self._user_id,
            service_id=self._create_appointment_dto.service_id,
            scheduled_at=self._create_appointment_dto.scheduled_at,
            notes=self._create_appointment_dto.notes,
        )
        return to_appointment_dto(appointment_entity)
