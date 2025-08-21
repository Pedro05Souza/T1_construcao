from t1_construcao.domain import UserRepository
from t1_construcao.application.dtos import CreateUserDto, UserResponseDto
from .assemblers import to_user_dto

__all__ = ["CreateUserUsecase"]


class CreateUserUsecase:

    def __init__(self, create_user_dto: CreateUserDto, user_repository: UserRepository):
        self._create_user_dto = create_user_dto
        self._user_repository = user_repository

    async def execute(self) -> UserResponseDto:
        user_entity = await self._user_repository.create(self._create_user_dto.name)
        return to_user_dto(user_entity)
