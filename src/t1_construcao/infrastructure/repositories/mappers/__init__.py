from t1_construcao.infrastructure.models.user import User
from t1_construcao.domain.entities import UserEntity

def user_model_to_entity(user_model: User) -> UserEntity:
    return UserEntity(
        id=str(user_model.id),
        name=user_model.name,
    )