from t1_construcao.application.dtos.user_dtos import UserResponseDto
from t1_construcao.application.usecases.assemblers.user_assembler import to_user_dto
from t1_construcao.domain import UserRepository

__all__ = ["GetUserByIdUsecase"]


class GetUserByIdUsecase:

    def __init__(self, user_id: str, user_repository: UserRepository):
        self._user_id = user_id
        self._user_repository = user_repository

    async def execute(self) -> UserResponseDto | None:
        user_entity = await self._user_repository.get_by_id(self._user_id)
        return to_user_dto(user_entity) if user_entity else None
