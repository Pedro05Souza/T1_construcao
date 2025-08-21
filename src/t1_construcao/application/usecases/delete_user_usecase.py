from t1_construcao.domain import UserRepository

__all__ = ["DeleteUserUsecase"]


class DeleteUserUsecase:

    def __init__(self, user_id: str, user_repository: UserRepository):
        self._user_id = user_id
        self._user_repository = user_repository

    async def execute(self) -> None:
        await self._user_repository.delete(self._user_id)
