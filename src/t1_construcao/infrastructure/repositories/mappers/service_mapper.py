from t1_construcao.infrastructure.models.service import Service
from t1_construcao.domain.entities.service_entity import ServiceEntity


def service_model_to_entity(service_model: Service) -> ServiceEntity:
    return ServiceEntity(
        id=str(service_model.id),
        name=service_model.name,
        description=service_model.description,
        duration_minutes=service_model.duration_minutes,
        price=service_model.price,
        is_active=service_model.is_active,
        created_at=service_model.created_at,
        updated_at=service_model.updated_at,
    )
