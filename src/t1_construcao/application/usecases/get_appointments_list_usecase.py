from t1_construcao.domain import AppointmentRepository
from t1_construcao.application.dtos import (
    AppointmentResponseDto,
    AppointmentListFilterDto,
)
from .assemblers.appointment_assembler import to_appointment_dto

__all__ = ["GetAppointmentsListUsecase"]


class GetAppointmentsListUsecase:

    def __init__(
        self,
        filter_dto: AppointmentListFilterDto,
        appointment_repository: AppointmentRepository,
    ):
        self._filter_dto = filter_dto
        self._appointment_repository = appointment_repository

    async def execute(self) -> tuple[list[AppointmentResponseDto], int]:
        appointments, total_count = await self._appointment_repository.get_all(
            user_id=self._filter_dto.user_id,
            service_id=self._filter_dto.service_id,
            status=self._filter_dto.status,
            start_date=self._filter_dto.start_date,
            end_date=self._filter_dto.end_date,
            page=self._filter_dto.page,
            page_size=self._filter_dto.page_size,
        )
        return [to_appointment_dto(apt) for apt in appointments], total_count
