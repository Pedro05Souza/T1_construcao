from t1_construcao.application.dtos.user_dtos import UserResponseDto, UserListFilterDto
from t1_construcao.application.usecases.assemblers.user_assembler import to_user_dto
from t1_construcao.domain import UserRepository

__all__ = ["GetUsersListUsecase"]


class GetUsersListUsecase:

    def __init__(self, filter_dto: UserListFilterDto, user_repository: UserRepository):
        self._filter_dto = filter_dto
        self._user_repository = user_repository

    async def execute(self) -> tuple[list[UserResponseDto], int]:
        users, total_count = await self._user_repository.get_all(
            role=self._filter_dto.role,
            name=self._filter_dto.name,
            page=self._filter_dto.page,
            page_size=self._filter_dto.page_size,
        )
        return [to_user_dto(user) for user in users], total_count
