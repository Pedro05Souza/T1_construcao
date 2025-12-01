from t1_construcao.infrastructure.models.user import User
from t1_construcao.domain.entities import UserEntity
from .service_mapper import service_model_to_entity
from .appointment_mapper import appointment_model_to_entity


def user_model_to_entity(user_model: User) -> UserEntity:
    return UserEntity(
        id=str(user_model.id),
        name=user_model.name,
        role=user_model.role,
    )


__all__ = [
    "user_model_to_entity",
    "service_model_to_entity",
    "appointment_model_to_entity",
]
