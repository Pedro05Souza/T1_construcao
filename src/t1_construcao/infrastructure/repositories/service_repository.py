from decimal import Decimal
from t1_construcao.domain import ServiceEntity, ServiceRepository
from ._repository_meta import RepositoryMeta
from ..models import Service
from .mappers import service_model_to_entity

__all__ = ["ServiceRepository"]


class ServiceRepository(metaclass=RepositoryMeta):

    async def create(
        self, name: str, description: str, duration_minutes: int, price: Decimal
    ) -> ServiceEntity:
        service = await Service.create(
            name=name,
            description=description,
            duration_minutes=duration_minutes,
            price=price,
        )
        return service_model_to_entity(service)

    async def update(
        self,
        service_id: str,
        name: str | None = None,
        description: str | None = None,
        duration_minutes: int | None = None,
        price: Decimal | None = None,
        is_active: bool | None = None,
    ) -> ServiceEntity:
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if duration_minutes is not None:
            update_data["duration_minutes"] = duration_minutes
        if price is not None:
            update_data["price"] = price
        if is_active is not None:
            update_data["is_active"] = is_active

        if update_data:
            updated = await Service.filter(id=service_id).update(**update_data)
            if not updated:
                raise ValueError("Service not found")

        service_entity = await self.get_by_id(service_id)
        if service_entity is None:
            raise ValueError("Service not found")
        return service_entity

    async def get_by_id(self, service_id: str) -> ServiceEntity | None:
        service = await Service.get(id=service_id)
        return service_model_to_entity(service) if service else None

    async def delete(self, service_id: str) -> None:
        deleted = await Service.filter(id=service_id).delete()
        if not deleted:
            raise ValueError("Service not found")
        return None

    async def get_all(
        self,
        is_active: bool | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[ServiceEntity], int]:
        query = Service.all()

        if is_active is not None:
            query = query.filter(is_active=is_active)
        if name is not None:
            query = query.filter(name__icontains=name)

        total_count = await query.count()

        offset = (page - 1) * page_size
        services = await query.offset(offset).limit(page_size)

        return [service_model_to_entity(service) for service in services], total_count
