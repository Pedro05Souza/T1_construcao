from t1_construcao.application.dtos import UserResponseDto
from t1_construcao.domain.entities import UserEntity

__all__ = ["to_user_dto"]


def to_user_dto(user_entity: UserEntity) -> UserResponseDto:
    """
    Converts a user entity to a UserResponseDto.

    Args:
        user_entity: The user entity to convert.

    Returns:
        UserResponseDto: The converted DTO.
    """
    return UserResponseDto(
        id=user_entity.id,
        name=user_entity.name,
    )
