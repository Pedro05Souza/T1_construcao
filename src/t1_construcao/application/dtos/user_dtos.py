from pydantic import BaseModel, Field


__all__ = ["CreateUserDto", "UpdateUserDto", "UserResponseDto", "UserListFilterDto"]


class CreateUserDto(BaseModel):
    name: str
    role: str = "client"  # admin, operator, client


class UpdateUserDto(BaseModel):
    name: str | None = None
    role: str | None = None


class UserResponseDto(BaseModel):
    id: str
    name: str
    role: str


class UserListFilterDto(BaseModel):
    role: str | None = None
    name: str | None = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
