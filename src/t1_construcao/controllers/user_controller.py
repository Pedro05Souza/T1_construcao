from fastapi import APIRouter, status, Depends, HTTPException, Query
from t1_construcao.application.usecases import (
    CreateUserUsecase,
    UpdateUserUsecase,
    GetUserByIdUsecase,
    DeleteUserUsecase,
    GetUsersListUsecase,
)
from t1_construcao.infrastructure import UserRepository
from t1_construcao.application.dtos import (
    CreateUserDto,
    UserResponseDto,
    UpdateUserDto,
    UserListFilterDto,
    PaginatedResponse,
)

from ..shared.auth import (
    get_admin_user,
    check_admin_or_self,
)

user_router = APIRouter(prefix="/users", tags=["users"], include_in_schema=True)


def get_repository():
    return UserRepository()


@user_router.get(
    "/",
    response_model=PaginatedResponse[UserResponseDto],
    summary="Listar usuários",
    description="Lista todos os usuários com paginação e filtros. Acesso restrito a administradores.",
)
async def list_users(
    role: str | None = Query(None),
    name: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _admin_payload: dict = Depends(get_admin_user),
) -> dict:
    """
    Endpoint para listar users com paginação e filtros.
    Acesso restrito a administradores.
    """
    filter_dto = UserListFilterDto(role=role, name=name, page=page, page_size=page_size)
    use_case = GetUsersListUsecase(filter_dto, UserRepository())
    users, total_count = await use_case.execute()

    return {
        "items": users,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size,
    }


@user_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    description="Cria um novo usuário. Acesso restrito a administradores.",
)
async def create_user(
    create_user_dto: CreateUserDto,
    repo: UserRepository = Depends(get_repository),
    _admin_payload: dict = Depends(get_admin_user),
) -> UserResponseDto:
    """
    Cria um novo user.
    Acesso restrito a administradores.
    """
    use_case = CreateUserUsecase(create_user_dto, repo)
    return await use_case.execute()


@user_router.put(
    "/{user_id}",
    response_model=UserResponseDto,
    summary="Atualizar usuário",
    description="Atualiza um usuário existente. Acesso permitido para administradores ou para o próprio usuário.",
)
async def update_user(
    user_id: str,
    update_user_dto: UpdateUserDto,
    repo: UserRepository = Depends(get_repository),
    _auth_payload: dict = Depends(check_admin_or_self),
) -> UserResponseDto:
    """
    Atualiza um user.
    Acesso permitido para administradores ou para o próprio user.
    """
    use_case = UpdateUserUsecase(user_id, update_user_dto, repo)
    return await use_case.execute()


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar usuário",
    description="Deleta um usuário. Acesso restrito a administradores.",
)
async def delete_user(
    user_id: str,
    repo: UserRepository = Depends(get_repository),
    _admin_payload: dict = Depends(get_admin_user),
) -> None:
    """
    Apaga um user.
    Acesso restrito a administradores.
    """
    use_case = DeleteUserUsecase(user_id, repo)
    await use_case.execute()


@user_router.get(
    "/{user_id}",
    response_model=UserResponseDto,
    summary="Obter usuário por ID",
    description="Obtém um usuário pelo seu ID. Acesso permitido para administradores ou para o próprio usuário.",
)
async def get_user_by_id(
    user_id: str,
    repo: UserRepository = Depends(get_repository),
    _auth_payload: dict = Depends(check_admin_or_self),
) -> UserResponseDto | None:
    """
    Obtém um user pelo seu ID.
    Acesso permitido para administradores ou para o próprio user.
    """
    use_case = GetUserByIdUsecase(user_id, repo)
    user = await use_case.execute()

    if not user:
        raise HTTPException(status_code=404, detail="User não encontrado")
    return user
