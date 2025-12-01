from t1_construcao.domain import ServiceRepository
from t1_construcao.application.dtos import ServiceResponseDto
from .assemblers.service_assembler import to_service_dto

__all__ = ["GetServiceByIdUsecase"]


class GetServiceByIdUsecase:

    def __init__(self, service_id: str, service_repository: ServiceRepository):
        self._service_id = service_id
        self._service_repository = service_repository

    async def execute(self) -> ServiceResponseDto | None:
        service_entity = await self._service_repository.get_by_id(self._service_id)
        return to_service_dto(service_entity) if service_entity else None
