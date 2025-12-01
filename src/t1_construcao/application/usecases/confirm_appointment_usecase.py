from t1_construcao.domain import AppointmentRepository
from t1_construcao.application.dtos import AppointmentResponseDto
from .assemblers.appointment_assembler import to_appointment_dto
from fastapi import HTTPException

__all__ = ["ConfirmAppointmentUsecase"]


class ConfirmAppointmentUsecase:

    def __init__(
        self, appointment_id: str, appointment_repository: AppointmentRepository
    ):
        self._appointment_id = appointment_id
        self._appointment_repository = appointment_repository

    async def execute(self) -> AppointmentResponseDto:
        appointment = await self._appointment_repository.get_by_id(self._appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if appointment.status != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot confirm appointment with status '{appointment.status}'",
            )

        appointment_entity = await self._appointment_repository.update(
            appointment_id=self._appointment_id, status="confirmed"
        )
        return to_appointment_dto(appointment_entity)
