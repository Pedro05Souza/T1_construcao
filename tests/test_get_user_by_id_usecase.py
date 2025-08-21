import pytest

from t1_construcao.application.usecases.get_user_by_id_usecase import GetUserByIdUsecase
from t1_construcao.application.dtos.user_dtos import UserResponseDto


class TestGetUserByIdUsecase:

    @pytest.mark.asyncio
    async def test_execute_user_found(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        user_id = existing_user.id
        usecase = GetUserByIdUsecase(user_id, mock_repository)

        result = await usecase.execute()

        assert isinstance(result, UserResponseDto)
        assert result.id == existing_user.id
        assert result.name == existing_user.name

        mock_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_execute_user_not_found(self, mock_user_repository):
        non_existing_id = "999"
        usecase = GetUserByIdUsecase(non_existing_id, mock_user_repository)

        result = await usecase.execute()

        assert result is None

        mock_user_repository.get_by_id.assert_called_once_with(non_existing_id)

    @pytest.mark.asyncio
    async def test_execute_with_valid_id_format(self, mock_user_repository):
        test_cases = ["1", "123", "abc", "user-123", "UUID-like-string"]

        for user_id in test_cases:
            mock_user_repository.get_by_id.reset_mock()
            usecase = GetUserByIdUsecase(user_id, mock_user_repository)

            result = await usecase.execute()

            assert result is None
            mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_execute_returns_correct_dto_structure(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        usecase = GetUserByIdUsecase(existing_user.id, mock_repository)

        result = await usecase.execute()

        assert result is not None
        assert hasattr(result, "id")
        assert hasattr(result, "name")
        assert isinstance(result.id, str)
        assert isinstance(result.name, str)

    @pytest.mark.asyncio
    async def test_execute_with_empty_id(self, mock_user_repository):
        empty_id = ""
        usecase = GetUserByIdUsecase(empty_id, mock_user_repository)

        result = await usecase.execute()

        assert result is None
        mock_user_repository.get_by_id.assert_called_once_with(empty_id)

    @pytest.mark.asyncio
    async def test_execute_repository_exception_propagation(self, mock_user_repository):
        user_id = "test-id"
        usecase = GetUserByIdUsecase(user_id, mock_user_repository)

        mock_user_repository.get_by_id.side_effect = Exception(
            "Database connection error"
        )

        with pytest.raises(Exception, match="Database connection error"):
            await usecase.execute()

    @pytest.mark.asyncio
    async def test_execute_multiple_users_get_correct_one(self, mock_user_repository):
        await mock_user_repository.create("User One")
        user2 = await mock_user_repository.create("User Two")
        await mock_user_repository.create("User Three")

        usecase = GetUserByIdUsecase(user2.id, mock_user_repository)

        result = await usecase.execute()

        assert result is not None
        assert result.id == user2.id
        assert result.name == user2.name
        assert result.name == "User Two"
