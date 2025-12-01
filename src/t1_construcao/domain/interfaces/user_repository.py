from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from src.t1_construcao.domain.entities.user_entity import UserEntity


__all__ = ["UserRepository"]


@runtime_checkable
class UserRepository(Protocol):
    async def create(self, name: str, role: str = "client") -> "UserEntity":
        """Create a new user with the given name and role."""
        ...

    async def update(
        self, user_id: str, name: str | None = None, role: str | None = None
    ) -> "UserEntity":
        """Update an existing user identified by user_id with the new name and/or role."""
        ...

    async def get_by_id(self, user_id: str) -> "UserEntity | None":
        """Retrieve a user by their ID, returning None if not found."""
        ...

    async def delete(self, user_id: str) -> None:
        """Delete a user by their ID."""
        ...

    async def get_all(
        self,
        role: str | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list["UserEntity"], int]:
        """Retrieve all users with pagination and filters. Returns (users, total_count)."""
        ...
