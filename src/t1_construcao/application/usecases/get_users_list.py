from t1_construcao.application.dtos.user_dtos import UserResponseDto
from t1_construcao.application.usecases.assemblers.user_assembler import to_user_dto
from t1_construcao.domain import UserRepository

__all__ = ["GetUsersListUsecase"]


class GetUsersListUsecase:

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self) -> list[UserResponseDto]:
        user_entities = await self._user_repository.get_all()
        return [to_user_dto(user) for user in user_entities]