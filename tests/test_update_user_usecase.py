import pytest

from t1_construcao.application.usecases.update_user_usecase import UpdateUserUsecase
from t1_construcao.application.dtos.user_dtos import UpdateUserDto, UserResponseDto


class TestUpdateUserUsecase:

    @pytest.mark.asyncio
    async def test_execute_success(self, repository_with_user, update_user_dto):
        mock_repository, existing_user = repository_with_user
        user_id = existing_user.id
        usecase = UpdateUserUsecase(user_id, update_user_dto, mock_repository)
        
        result = await usecase.execute()
        
        assert isinstance(result, UserResponseDto)
        assert result.id == user_id
        assert result.name == update_user_dto.name
        
        mock_repository.update.assert_called_once_with(user_id, update_user_dto.name)

    @pytest.mark.asyncio
    async def test_execute_updates_existing_user(self, mock_user_repository):
        original_user = await mock_user_repository.create("Original Name")
        
        new_name = "Updated Name"
        update_dto = UpdateUserDto(name=new_name)
        usecase = UpdateUserUsecase(original_user.id, update_dto, mock_user_repository)
        
        result = await usecase.execute()
        
        assert result.id == original_user.id
        assert result.name == new_name
        assert result.name != "Original Name"

    @pytest.mark.asyncio
    async def test_execute_with_same_name(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        same_name_dto = UpdateUserDto(name=existing_user.name)
        usecase = UpdateUserUsecase(existing_user.id, same_name_dto, mock_repository)
        
        result = await usecase.execute()
        
        assert result.id == existing_user.id
        assert result.name == existing_user.name
        mock_repository.update.assert_called_once_with(existing_user.id, existing_user.name)

    @pytest.mark.asyncio
    async def test_execute_with_empty_name(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        empty_name_dto = UpdateUserDto(name="")
        usecase = UpdateUserUsecase(existing_user.id, empty_name_dto, mock_repository)
        
        result = await usecase.execute()
        
        assert result.id == existing_user.id
        assert result.name == ""
        mock_repository.update.assert_called_once_with(existing_user.id, "")

    @pytest.mark.asyncio
    async def test_execute_with_special_characters(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        special_name = "María José & Associates @#$%"
        special_name_dto = UpdateUserDto(name=special_name)
        usecase = UpdateUserUsecase(existing_user.id, special_name_dto, mock_repository)
        
        result = await usecase.execute()
        
        assert result.id == existing_user.id
        assert result.name == special_name
        mock_repository.update.assert_called_once_with(existing_user.id, special_name)

    @pytest.mark.asyncio
    async def test_execute_returns_correct_dto_structure(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        update_dto = UpdateUserDto(name="New Name")
        usecase = UpdateUserUsecase(existing_user.id, update_dto, mock_repository)
        
        result = await usecase.execute()
        
        assert hasattr(result, 'id')
        assert hasattr(result, 'name')
        assert isinstance(result.id, str)
        assert isinstance(result.name, str)

    @pytest.mark.asyncio
    async def test_execute_with_nonexistent_user_id(self, mock_user_repository):
        non_existent_id = "999"
        update_dto = UpdateUserDto(name="New Name")
        usecase = UpdateUserUsecase(non_existent_id, update_dto, mock_user_repository)
        
        mock_user_repository.update.side_effect = ValueError(f"User with id {non_existent_id} not found")
        
        with pytest.raises(ValueError, match="User with id 999 not found"):
            await usecase.execute()

    @pytest.mark.asyncio
    async def test_execute_repository_exception_propagation(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        update_dto = UpdateUserDto(name="New Name")
        usecase = UpdateUserUsecase(existing_user.id, update_dto, mock_repository)
        
        mock_repository.update.side_effect = Exception("Database update error")
        
        with pytest.raises(Exception, match="Database update error"):
            await usecase.execute()

    @pytest.mark.asyncio
    async def test_execute_with_very_long_name(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        long_name = "A" * 1000
        long_name_dto = UpdateUserDto(name=long_name)
        usecase = UpdateUserUsecase(existing_user.id, long_name_dto, mock_repository)
        
        result = await usecase.execute()
        
        assert result.id == existing_user.id
        assert result.name == long_name
        assert len(result.name) == 1000
