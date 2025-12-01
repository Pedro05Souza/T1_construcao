from typing import Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada padrão para listagens."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 10,
                "total_pages": 0,
            }
        }
    )

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# Versões específicas para melhor compatibilidade com OpenAPI
def create_paginated_response_model(item_model):
    """Cria um modelo de resposta paginada específico para um tipo de item."""

    class SpecificPaginatedResponse(BaseModel):
        items: List[item_model]
        total: int
        page: int
        page_size: int
        total_pages: int

        class Config:
            json_schema_extra = {
                "example": {
                    "items": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 0,
                }
            }

    return SpecificPaginatedResponse
