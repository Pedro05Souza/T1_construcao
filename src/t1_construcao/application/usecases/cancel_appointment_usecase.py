from t1_construcao.domain import AppointmentRepository
from t1_construcao.application.dtos import CancelAppointmentDto, AppointmentResponseDto
from .assemblers.appointment_assembler import to_appointment_dto
from fastapi import HTTPException

__all__ = ["CancelAppointmentUsecase"]


class CancelAppointmentUsecase:

    def __init__(
        self,
        appointment_id: str,
        cancel_appointment_dto: CancelAppointmentDto,
        appointment_repository: AppointmentRepository,
    ):
        self._appointment_id = appointment_id
        self._cancel_appointment_dto = cancel_appointment_dto
        self._appointment_repository = appointment_repository

    async def execute(self) -> AppointmentResponseDto:
        appointment = await self._appointment_repository.get_by_id(self._appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if appointment.status == "cancelled":
            raise HTTPException(
                status_code=400, detail="Appointment is already cancelled"
            )

        if appointment.status == "completed":
            raise HTTPException(
                status_code=400, detail="Cannot cancel a completed appointment"
            )

        notes = appointment.notes or ""
        if self._cancel_appointment_dto.reason:
            notes = f"{notes}\n[Cancellation reason: {self._cancel_appointment_dto.reason}]".strip()

        appointment_entity = await self._appointment_repository.update(
            appointment_id=self._appointment_id, status="cancelled", notes=notes
        )
        return to_appointment_dto(appointment_entity)
