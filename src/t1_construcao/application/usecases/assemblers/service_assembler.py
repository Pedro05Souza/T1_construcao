from t1_construcao.application.dtos import ServiceResponseDto
from t1_construcao.domain.entities import ServiceEntity

__all__ = ["to_service_dto"]


def to_service_dto(service_entity: ServiceEntity) -> ServiceResponseDto:
    return ServiceResponseDto(
        id=service_entity.id,
        name=service_entity.name,
        description=service_entity.description,
        duration_minutes=service_entity.duration_minutes,
        price=service_entity.price,
        is_active=service_entity.is_active,
        created_at=service_entity.created_at,
        updated_at=service_entity.updated_at,
    )
