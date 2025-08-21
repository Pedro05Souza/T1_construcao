from ._repository_meta import RepositoryMeta
from t1_construcao.domain import UserEntity
from ..models import User
from .mappers import user_model_to_entity

__all__ = ["UserRepository"]


class UserRepository(metaclass=RepositoryMeta):

    async def create(self, name: str) -> UserEntity:
        user = await User.create(name=name)
        return user_model_to_entity(user)

    async def update(self, user_id: str, name: str) -> UserEntity:
        user = await User.filter(id=user_id).update(name=name)
        if not user:
            raise ValueError("User not found")

        user_entity = await self.get_by_id(user_id)
        if user_entity is None:
            raise ValueError("User not found")
        return user_entity

    async def get_by_id(self, user_id: str) -> UserEntity | None:
        user = await User.get(id=user_id)
        return user_model_to_entity(user) if user else None

    async def delete(self, user_id: str) -> None:
        user = await User.filter(id=user_id).delete()
        if not user:
            raise ValueError("User not found")
        return None
