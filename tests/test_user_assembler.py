from t1_construcao.application.usecases.assemblers.user_assembler import to_user_dto
from t1_construcao.application.dtos.user_dtos import UserResponseDto
from t1_construcao.domain.entities.user_entity import UserEntity


class TestUserAssembler:

    def test_to_user_dto_success(self, sample_user_entity):
        result = to_user_dto(sample_user_entity)
        
        assert isinstance(result, UserResponseDto)
        assert result.id == sample_user_entity.id
        assert result.name == sample_user_entity.name

    def test_to_user_dto_with_different_values(self):
        test_cases = [
            UserEntity(id="1", name="John Doe"),
            UserEntity(id="abc123", name="Jane Smith"),
            UserEntity(id="999", name=""),
            UserEntity(id="special-id", name="Special @#$ Characters"),
            UserEntity(id="long-id-12345", name="A" * 100),
        ]
        
        for entity in test_cases:
            result = to_user_dto(entity)
            
            assert isinstance(result, UserResponseDto)
            assert result.id == entity.id
            assert result.name == entity.name

    def test_to_user_dto_preserves_data_types(self):
        entity = UserEntity(id="123", name="Test User")
        
        result = to_user_dto(entity)
        
        assert isinstance(result.id, str)
        assert isinstance(result.name, str)

    def test_to_user_dto_with_empty_values(self):
        entity = UserEntity(id="", name="")
        
        result = to_user_dto(entity)
        
        assert result.id == ""
        assert result.name == ""

    def test_to_user_dto_structure_completeness(self):
        entity = UserEntity(id="test-id", name="Test Name")
        
        result = to_user_dto(entity)
        
        assert hasattr(result, 'id')
        assert hasattr(result, 'name')
        expected_attrs = {'id', 'name'}
        actual_attrs = set(result.__dict__.keys())
        assert actual_attrs == expected_attrs
