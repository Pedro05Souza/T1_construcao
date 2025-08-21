from abc import ABC
from dataclasses import dataclass


@dataclass
class BaseEntity(ABC):
    """
    Base class for all entities in the domain layer.
    This class serves as a marker for domain entities and can be extended
    to include common functionality or properties for all entities.
    """

    id: str
