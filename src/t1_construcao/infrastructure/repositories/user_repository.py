from ._repository_meta import RepositoryMeta
from t1_construcao.domain import UserEntity
from ..models import User
from .mappers import user_model_to_entity

class UserRepository(metaclass=RepositoryMeta):
    
    async def create(self, name: str) -> UserEntity:
        user = await User.create(name=name)
        return user_model_to_entity(user)

    async def get_by_id(self, user_id: str) -> UserEntity | None:
        user = await User.get(id=user_id)
        return user_model_to_entity(user) if user else None