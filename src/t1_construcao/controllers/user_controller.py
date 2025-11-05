from fastapi import APIRouter, status, Depends, HTTPException
from t1_construcao.application.usecases import (
    CreateUserUsecase,
    UpdateUserUsecase,
    GetUserByIdUsecase,
    DeleteUserUsecase,
    GetUsersListUsecase,
)
from t1_construcao.infrastructure import UserRepository
from t1_construcao.application.dtos import CreateUserDto, UserResponseDto, UpdateUserDto

from ..shared.auth import (
    get_admin_user,
    check_admin_or_self,
)

user_router = APIRouter(prefix="/users", tags=["users"])


def get_repository():
    return UserRepository()


@user_router.get("/", response_model=list[UserResponseDto])
async def list_users(
    _repo: UserRepository = Depends(get_repository),
    admin_payload: dict = Depends(get_admin_user)
) -> list[UserResponseDto]:
    """
    Endpoint para listar todos os users.
    Acesso restrito a administradores.
    """
    use_case = GetUsersListUsecase(_repo)
    return await use_case.execute()

@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user_dto: CreateUserDto,
    repo: UserRepository = Depends(get_repository),
    _admin_payload: dict = Depends(get_admin_user)
) -> UserResponseDto:
    """
    Cria um novo user.
    Acesso restrito a administradores.
    """
    use_case = CreateUserUsecase(create_user_dto, repo)
    return await use_case.execute()


@user_router.put("/{user_id}", response_model=UserResponseDto)
async def update_user(
    user_id: str, 
    update_user_dto: UpdateUserDto,
    repo: UserRepository = Depends(get_repository),
    _auth_payload: dict = Depends(check_admin_or_self) 
) -> UserResponseDto:
    """
    Atualiza um user.
    Acesso permitido para administradores ou para o próprio user.
    """
    use_case = UpdateUserUsecase(user_id, update_user_dto, repo)
    return await use_case.execute()


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    repo: UserRepository = Depends(get_repository),
    _admin_payload: dict = Depends(get_admin_user)
) -> None:
    """
    Apaga um user.
    Acesso restrito a administradores.
    """
    use_case = DeleteUserUsecase(user_id, repo)
    await use_case.execute()


@user_router.get("/{user_id}", response_model=UserResponseDto)
async def get_user_by_id(
    user_id: str, 
    repo: UserRepository = Depends(get_repository),
    _auth_payload: dict = Depends(check_admin_or_self)
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