from dataclasses import dataclass
from t1_construcao.domain.entities.base_entity import BaseEntity

__all__ = ["UserEntity"]

@dataclass
class UserEntity(BaseEntity):
    name: str