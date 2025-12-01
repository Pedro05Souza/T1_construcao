from t1_construcao.domain import ServiceRepository
from t1_construcao.application.dtos import ServiceResponseDto, ServiceListFilterDto
from .assemblers.service_assembler import to_service_dto

__all__ = ["GetServicesListUsecase"]


class GetServicesListUsecase:

    def __init__(
        self, filter_dto: ServiceListFilterDto, service_repository: ServiceRepository
    ):
        self._filter_dto = filter_dto
        self._service_repository = service_repository

    async def execute(self) -> tuple[list[ServiceResponseDto], int]:
        services, total_count = await self._service_repository.get_all(
            is_active=self._filter_dto.is_active,
            name=self._filter_dto.name,
            page=self._filter_dto.page,
            page_size=self._filter_dto.page_size,
        )
        return [to_service_dto(service) for service in services], total_count
