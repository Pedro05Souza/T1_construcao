from t1_construcao.domain import UserEntity
from ._repository_meta import RepositoryMeta
from ..models import User
from .mappers import user_model_to_entity

__all__ = ["UserRepository"]


class UserRepository(metaclass=RepositoryMeta):

    async def create(self, name: str, role: str = "client") -> UserEntity:
        user = await User.create(name=name, role=role)
        return user_model_to_entity(user)

    async def update(
        self, user_id: str, name: str | None = None, role: str | None = None
    ) -> UserEntity:
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if role is not None:
            update_data["role"] = role

        if update_data:
            user = await User.filter(id=user_id).update(**update_data)
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

    async def get_all(
        self,
        role: str | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[UserEntity], int]:
        query = User.all()

        if role is not None:
            query = query.filter(role=role)
        if name is not None:
            query = query.filter(name__icontains=name)

        total_count = await query.count()

        offset = (page - 1) * page_size
        users = await query.offset(offset).limit(page_size)

        return [user_model_to_entity(user) for user in users], total_count
