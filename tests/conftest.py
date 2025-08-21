from typing import Optional
from unittest.mock import AsyncMock
import pytest

from t1_construcao.domain.entities.user_entity import UserEntity
from t1_construcao.application.dtos.user_dtos import (
    CreateUserDto,
    UpdateUserDto,
    UserResponseDto,
)


class MockUserRepository:

    def __init__(self):
        self.users: dict[str, UserEntity] = {}
        self.next_id = 1

        self.create = AsyncMock(side_effect=self._create)
        self.update = AsyncMock(side_effect=self._update)
        self.get_by_id = AsyncMock(side_effect=self._get_by_id)
        self.delete = AsyncMock(side_effect=self._delete)

    async def _create(self, name: str) -> UserEntity:
        user_id = str(self.next_id)
        self.next_id += 1
        user = UserEntity(id=user_id, name=name)
        self.users[user_id] = user
        return user

    async def _update(self, user_id: str, name: str) -> UserEntity:
        if user_id not in self.users:
            raise ValueError(f"User with id {user_id} not found")

        user = self.users[user_id]
        updated_user = UserEntity(id=user.id, name=name)
        self.users[user_id] = updated_user
        return updated_user

    async def _get_by_id(self, user_id: str) -> Optional[UserEntity]:
        return self.users.get(user_id)

    async def _delete(self, user_id: str) -> None:
        if user_id in self.users:
            del self.users[user_id]


@pytest.fixture
def mock_user_repository():
    return MockUserRepository()


@pytest.fixture
def sample_user_entity():
    return UserEntity(id="1", name="John Doe")


@pytest.fixture
def create_user_dto():
    return CreateUserDto(name="Jane Smith")


@pytest.fixture
def update_user_dto():
    return UpdateUserDto(name="Jane Smith Updated")


@pytest.fixture
def user_response_dto():
    return UserResponseDto(id="1", name="John Doe")


@pytest.fixture
async def repository_with_user(mock_user_repository): #pylint: disable=redefined-outer-name
    user = await mock_user_repository.create("Existing User")
    return mock_user_repository, user
