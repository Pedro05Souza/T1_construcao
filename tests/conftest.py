from typing import Optional
from unittest.mock import AsyncMock
import os
import pytest
from tortoise import Tortoise

from t1_construcao.domain.entities.user_entity import UserEntity
from t1_construcao.application.dtos.user_dtos import (
    CreateUserDto,
    UpdateUserDto,
    UserResponseDto,
)
from t1_construcao.infrastructure.repositories.user_repository import (
    UserRepository as TortoiseUserRepository,
)


class MockUserRepository:

    def __init__(self):
        self.users: dict[str, UserEntity] = {}
        self.next_id = 1

        self.create = AsyncMock(side_effect=self._create)
        self.update = AsyncMock(side_effect=self._update)
        self.get_by_id = AsyncMock(side_effect=self._get_by_id)
        self.get_all = AsyncMock(side_effect=self._get_all)
        self.delete = AsyncMock(side_effect=self._delete)

    async def _create(self, name: str, role: str = "client") -> UserEntity:
        user_id = str(self.next_id)
        self.next_id += 1
        user = UserEntity(id=user_id, name=name, role=role)
        self.users[user_id] = user
        return user

    async def _update(
        self, user_id: str, name: str | None = None, role: str | None = None
    ) -> UserEntity:
        if user_id not in self.users:
            raise ValueError(f"User with id {user_id} not found")

        user = self.users[user_id]
        updated_name = name if name is not None else user.name
        updated_role = role if role is not None else user.role
        updated_user = UserEntity(id=user.id, name=updated_name, role=updated_role)
        self.users[user_id] = updated_user
        return updated_user

    async def _get_by_id(self, user_id: str) -> Optional[UserEntity]:
        return self.users.get(user_id)

    async def _get_all(
        self,
        role: str | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[UserEntity], int]:
        filtered = list(self.users.values())

        if role is not None:
            filtered = [u for u in filtered if u.role == role]
        if name is not None:
            filtered = [u for u in filtered if name.lower() in u.name.lower()]

        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = filtered[start:end]

        return paginated, total

    async def _delete(self, user_id: str) -> None:
        if user_id in self.users:
            del self.users[user_id]


@pytest.fixture
def mock_user_repository():
    return MockUserRepository()


@pytest.fixture
def sample_user_entity():
    return UserEntity(id="1", name="John Doe", role="client")


@pytest.fixture
def create_user_dto():
    return CreateUserDto(name="Jane Smith")


@pytest.fixture
def update_user_dto():
    return UpdateUserDto(name="Jane Smith Updated")


@pytest.fixture
def user_response_dto():
    return UserResponseDto(id="1", name="John Doe", role="client")


@pytest.fixture
async def repository_with_user(
    mock_user_repository,
):  # pylint: disable=redefined-outer-name
    user = await mock_user_repository.create("Existing User")
    return mock_user_repository, user


# Database fixtures for integration tests
@pytest.fixture(scope="session")
async def db_connection():
    """Initialize database connection for tests using Docker test_db."""
    # Use test database URL from environment or default to Docker test_db
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgres://postgres:postgres@localhost:5433/t1_construcao_test",
    )

    tortoise_config = {
        "connections": {"default": test_db_url},
        "apps": {
            "models": {
                "models": ["t1_construcao.infrastructure.models", "aerich.models"],
                "default_connection": "default",
            }
        },
    }

    await Tortoise.init(config=tortoise_config)
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()


@pytest.fixture
async def db_repository(db_connection):  # pylint: disable=redefined-outer-name
    """Provides a real database repository for integration tests."""
    return TortoiseUserRepository()


@pytest.fixture
async def clean_db(db_connection):  # pylint: disable=redefined-outer-name
    """Clean database before each test."""
    from t1_construcao.infrastructure.models.user import User
    from t1_construcao.infrastructure.models.service import Service
    from t1_construcao.infrastructure.models.appointment import Appointment

    # Clean all tables
    await Appointment.all().delete()
    await Service.all().delete()
    await User.all().delete()

    yield

    # Clean after test as well
    await Appointment.all().delete()
    await Service.all().delete()
    await User.all().delete()
