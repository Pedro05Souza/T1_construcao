from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from src.t1_construcao.domain.entities.user_entity import UserEntity


__all__ = ["UserRepository"]


@runtime_checkable
class UserRepository(Protocol):
    async def create(self, name: str) -> "UserEntity":
        """Create a new user with the given name."""
        ...

    async def update(self, user_id: str, name: str) -> "UserEntity":
        """Update an existing user identified by user_id with the new name."""
        ...

    async def get_by_id(self, user_id: str) -> "UserEntity | None":
        """Retrieve a user by their ID, returning None if not found."""
        ...

    async def delete(self, user_id: str) -> None:
        """Delete a user by their ID."""
        ...
