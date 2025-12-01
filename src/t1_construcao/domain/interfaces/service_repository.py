from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal

if TYPE_CHECKING:
    from src.t1_construcao.domain.entities.service_entity import ServiceEntity


__all__ = ["ServiceRepository"]


@runtime_checkable
class ServiceRepository(Protocol):
    async def create(
        self, name: str, description: str, duration_minutes: int, price: Decimal
    ) -> "ServiceEntity":
        """Create a new service."""
        ...

    async def update(
        self,
        service_id: str,
        name: str | None = None,
        description: str | None = None,
        duration_minutes: int | None = None,
        price: Decimal | None = None,
        is_active: bool | None = None,
    ) -> "ServiceEntity":
        """Update an existing service."""
        ...

    async def get_by_id(self, service_id: str) -> "ServiceEntity | None":
        """Retrieve a service by its ID."""
        ...

    async def delete(self, service_id: str) -> None:
        """Delete a service by its ID."""
        ...

    async def get_all(
        self,
        is_active: bool | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list["ServiceEntity"], int]:
        """Retrieve all services with pagination and filters. Returns (services, total_count)."""
        ...
