import pytest

from t1_construcao.application.usecases.delete_user_usecase import DeleteUserUsecase


class TestDeleteUserUsecase:

    @pytest.mark.asyncio
    async def test_execute_success(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        user_id = existing_user.id
        usecase = DeleteUserUsecase(user_id, mock_repository)
        
        user_before_delete = await mock_repository.get_by_id(user_id)
        assert user_before_delete is not None
        
        result = await usecase.execute()
        
        assert result is None
        
        mock_repository.delete.assert_called_once_with(user_id)
        
        user_after_delete = await mock_repository.get_by_id(user_id)
        assert user_after_delete is None

    @pytest.mark.asyncio
    async def test_execute_with_existing_user(self, mock_user_repository):
        user = await mock_user_repository.create("User to Delete")
        user_id = user.id
        usecase = DeleteUserUsecase(user_id, mock_user_repository)
        
        assert await mock_user_repository.get_by_id(user_id) is not None
        
        await usecase.execute()
        
        assert await mock_user_repository.get_by_id(user_id) is None

    @pytest.mark.asyncio
    async def test_execute_with_nonexistent_user(self, mock_user_repository):
        non_existent_id = "999"
        usecase = DeleteUserUsecase(non_existent_id, mock_user_repository)
        
        result = await usecase.execute()
        
        assert result is None
        mock_user_repository.delete.assert_called_once_with(non_existent_id)

    @pytest.mark.asyncio
    async def test_execute_returns_none(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        usecase = DeleteUserUsecase(existing_user.id, mock_repository)
        
        result = await usecase.execute()
        
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_with_empty_id(self, mock_user_repository):
        empty_id = ""
        usecase = DeleteUserUsecase(empty_id, mock_user_repository)
        
        result = await usecase.execute()
        
        assert result is None
        mock_user_repository.delete.assert_called_once_with(empty_id)

    @pytest.mark.asyncio
    async def test_execute_with_various_id_formats(self, mock_user_repository):
        test_ids = ["1", "123", "abc", "user-123", "UUID-like-string"]
        
        for user_id in test_ids:
            mock_user_repository.delete.reset_mock()
            usecase = DeleteUserUsecase(user_id, mock_user_repository)
            
            result = await usecase.execute()
            
            assert result is None
            mock_user_repository.delete.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_execute_repository_exception_propagation(self, mock_user_repository):
        user_id = "test-id"
        usecase = DeleteUserUsecase(user_id, mock_user_repository)
        
        mock_user_repository.delete.side_effect = Exception("Database deletion error")
        
        with pytest.raises(Exception, match="Database deletion error"):
            await usecase.execute()

    @pytest.mark.asyncio
    async def test_execute_multiple_deletions_of_same_user(self, repository_with_user):
        mock_repository, existing_user = repository_with_user
        user_id = existing_user.id
        usecase = DeleteUserUsecase(user_id, mock_repository)
        
        await usecase.execute()
        
        mock_repository.delete.reset_mock()
        
        await usecase.execute()
        
        mock_repository.delete.assert_called_once_with(user_id)
        assert await mock_repository.get_by_id(user_id) is None

    @pytest.mark.asyncio
    async def test_execute_does_not_affect_other_users(self, mock_user_repository):
        user1 = await mock_user_repository.create("User 1")
        user2 = await mock_user_repository.create("User 2")
        user3 = await mock_user_repository.create("User 3")
        
        usecase = DeleteUserUsecase(user2.id, mock_user_repository)
        
        await usecase.execute()
        
        assert await mock_user_repository.get_by_id(user2.id) is None
        
        assert await mock_user_repository.get_by_id(user1.id) is not None
        assert await mock_user_repository.get_by_id(user3.id) is not None
