from t1_construcao.domain import UserRepository
from t1_construcao.application.dtos import UpdateUserDto, UserResponseDto
from .assemblers import to_user_dto

__all__ = ["UpdateUserUsecase"]


class UpdateUserUsecase:

    def __init__(
        self,
        user_id: str,
        update_user_dto: UpdateUserDto,
        user_repository: UserRepository,
    ):
        self._update_user_dto = update_user_dto
        self._user_repository = user_repository
        self._user_id = user_id

    async def execute(self) -> UserResponseDto:
        user_entity = await self._user_repository.update(
            self._user_id,
            name=self._update_user_dto.name,
            role=self._update_user_dto.role,
        )
        return to_user_dto(user_entity)
