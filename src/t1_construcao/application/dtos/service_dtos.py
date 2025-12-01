from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


__all__ = [
    "CreateServiceDto",
    "UpdateServiceDto",
    "ServiceResponseDto",
    "ServiceListFilterDto",
]


class CreateServiceDto(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    duration_minutes: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)


class UpdateServiceDto(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_minutes: int | None = Field(None, gt=0)
    price: Decimal | None = Field(None, gt=0)
    is_active: bool | None = None


class ServiceResponseDto(BaseModel):
    id: str
    name: str
    description: str
    duration_minutes: int
    price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ServiceListFilterDto(BaseModel):
    is_active: bool | None = None
    name: str | None = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
