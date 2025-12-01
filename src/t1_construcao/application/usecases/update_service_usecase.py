from t1_construcao.domain import ServiceRepository
from t1_construcao.application.dtos import UpdateServiceDto, ServiceResponseDto
from .assemblers.service_assembler import to_service_dto

__all__ = ["UpdateServiceUsecase"]


class UpdateServiceUsecase:

    def __init__(
        self,
        service_id: str,
        update_service_dto: UpdateServiceDto,
        service_repository: ServiceRepository,
    ):
        self._service_id = service_id
        self._update_service_dto = update_service_dto
        self._service_repository = service_repository

    async def execute(self) -> ServiceResponseDto:
        service_entity = await self._service_repository.update(
            self._service_id,
            name=self._update_service_dto.name,
            description=self._update_service_dto.description,
            duration_minutes=self._update_service_dto.duration_minutes,
            price=self._update_service_dto.price,
            is_active=self._update_service_dto.is_active,
        )
        return to_service_dto(service_entity)
