from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from t1_construcao.domain.entities.base_entity import BaseEntity

__all__ = ["ServiceEntity"]


@dataclass
class ServiceEntity(BaseEntity):
    name: str
    description: str
    duration_minutes: int
    price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
