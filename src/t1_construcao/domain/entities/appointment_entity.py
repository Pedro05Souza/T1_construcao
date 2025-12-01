from dataclasses import dataclass
from datetime import datetime
from t1_construcao.domain.entities.base_entity import BaseEntity

__all__ = ["AppointmentEntity"]


@dataclass
class AppointmentEntity(BaseEntity):
    user_id: str
    service_id: str
    scheduled_at: datetime
    status: str  # pending, confirmed, cancelled, completed
    notes: str | None
    created_at: datetime
    updated_at: datetime
