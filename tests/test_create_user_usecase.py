import pytest

from t1_construcao.application.usecases.create_user_usecase import CreateUserUsecase
from t1_construcao.application.dtos.user_dtos import CreateUserDto, UserResponseDto


class TestCreateUserUsecase:

    @pytest.mark.asyncio
    async def test_execute_success(self, mock_user_repository, create_user_dto):
        usecase = CreateUserUsecase(create_user_dto, mock_user_repository)

        result = await usecase.execute()

        assert isinstance(result, UserResponseDto)
        assert result.name == create_user_dto.name
        assert result.id == "1"

        mock_user_repository.create.assert_called_once_with(
            create_user_dto.name, create_user_dto.role
        )

    @pytest.mark.asyncio
    async def test_execute_repository_creates_user_with_correct_name(
        self, mock_user_repository
    ):
        user_name = "Test User"
        create_dto = CreateUserDto(name=user_name)
        usecase = CreateUserUsecase(create_dto, mock_user_repository)

        await usecase.execute()

        mock_user_repository.create.assert_called_once_with(user_name, "client")

    @pytest.mark.asyncio
    async def test_execute_returns_correct_dto_structure(self, mock_user_repository):
        create_dto = CreateUserDto(name="Another User")
        usecase = CreateUserUsecase(create_dto, mock_user_repository)

        result = await usecase.execute()

        assert hasattr(result, "id")
        assert hasattr(result, "name")
        assert isinstance(result.id, str)
        assert isinstance(result.name, str)
        assert result.name == "Another User"

    @pytest.mark.asyncio
    async def test_execute_with_empty_name(self, mock_user_repository):
        create_dto = CreateUserDto(name="")
        usecase = CreateUserUsecase(create_dto, mock_user_repository)

        result = await usecase.execute()

        assert result.name == ""
        mock_user_repository.create.assert_called_once_with("", "client")

    @pytest.mark.asyncio
    async def test_execute_with_special_characters_in_name(self, mock_user_repository):
        special_name = "João Silva & Co. @#$%"
        create_dto = CreateUserDto(name=special_name)
        usecase = CreateUserUsecase(create_dto, mock_user_repository)

        result = await usecase.execute()

        assert result.name == special_name
        mock_user_repository.create.assert_called_once_with(special_name, "client")

    @pytest.mark.asyncio
    async def test_execute_repository_exception_propagation(self, mock_user_repository):
        create_dto = CreateUserDto(name="Test User")
        usecase = CreateUserUsecase(create_dto, mock_user_repository)

        mock_user_repository.create.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await usecase.execute()
