from t1_construcao.domain import ServiceRepository
from t1_construcao.application.dtos import CreateServiceDto, ServiceResponseDto
from .assemblers.service_assembler import to_service_dto

__all__ = ["CreateServiceUsecase"]


class CreateServiceUsecase:

    def __init__(
        self,
        create_service_dto: CreateServiceDto,
        service_repository: ServiceRepository,
    ):
        self._create_service_dto = create_service_dto
        self._service_repository = service_repository

    async def execute(self) -> ServiceResponseDto:
        service_entity = await self._service_repository.create(
            name=self._create_service_dto.name,
            description=self._create_service_dto.description,
            duration_minutes=self._create_service_dto.duration_minutes,
            price=self._create_service_dto.price,
        )
        return to_service_dto(service_entity)
