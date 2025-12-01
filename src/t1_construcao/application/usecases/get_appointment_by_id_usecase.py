from t1_construcao.domain import AppointmentRepository
from t1_construcao.application.dtos import AppointmentResponseDto
from .assemblers.appointment_assembler import to_appointment_dto

__all__ = ["GetAppointmentByIdUsecase"]


class GetAppointmentByIdUsecase:

    def __init__(
        self, appointment_id: str, appointment_repository: AppointmentRepository
    ):
        self._appointment_id = appointment_id
        self._appointment_repository = appointment_repository

    async def execute(self) -> AppointmentResponseDto | None:
        appointment_entity = await self._appointment_repository.get_by_id(
            self._appointment_id
        )
        return to_appointment_dto(appointment_entity) if appointment_entity else None
