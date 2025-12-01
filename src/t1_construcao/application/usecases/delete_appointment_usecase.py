from t1_construcao.domain import AppointmentRepository

__all__ = ["DeleteAppointmentUsecase"]


class DeleteAppointmentUsecase:

    def __init__(
        self, appointment_id: str, appointment_repository: AppointmentRepository
    ):
        self._appointment_id = appointment_id
        self._appointment_repository = appointment_repository

    async def execute(self) -> None:
        await self._appointment_repository.delete(self._appointment_id)
