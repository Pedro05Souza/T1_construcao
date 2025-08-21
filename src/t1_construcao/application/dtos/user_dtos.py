from pydantic import BaseModel


__all__ = ["CreateUserDto", "UpdateUserDto", "UserResponseDto"]


class CreateUserDto(BaseModel):
    name: str


class UpdateUserDto(BaseModel):
    name: str


class UserResponseDto(BaseModel):
    id: str
    name: str
