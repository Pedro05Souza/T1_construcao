from fastapi import APIRouter, status
from t1_construcao.application.usecases import (
    CreateUserUsecase,
    UpdateUserUsecase,
    GetUserByIdUsecase,
    DeleteUserUsecase,
)
from t1_construcao.infrastructure import UserRepository
from t1_construcao.application.dtos import CreateUserDto, UserResponseDto, UpdateUserDto

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_dto: CreateUserDto) -> UserResponseDto:
    use_case = CreateUserUsecase(create_user_dto, UserRepository())
    return await use_case.execute()


@user_router.put("/{user_id}", response_model=UserResponseDto)
async def update_user(user_id: str, update_user_dto: UpdateUserDto) -> UserResponseDto:
    use_case = UpdateUserUsecase(user_id, update_user_dto, UserRepository())
    return await use_case.execute()


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str) -> None:
    use_case = DeleteUserUsecase(user_id, UserRepository())
    await use_case.execute()


@user_router.get("/{user_id}", response_model=UserResponseDto)
async def get_user_by_id(user_id: str) -> UserResponseDto | None:
    use_case = GetUserByIdUsecase(user_id, UserRepository())
    return await use_case.execute()
