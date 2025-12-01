from fastapi import APIRouter, status, Depends, HTTPException, Query
from t1_construcao.application.usecases import (
    CreateServiceUsecase,
    UpdateServiceUsecase,
    GetServiceByIdUsecase,
    GetServicesListUsecase,
    DeleteServiceUsecase,
)
from t1_construcao.infrastructure import ServiceRepository
from t1_construcao.application.dtos import (
    CreateServiceDto,
    ServiceResponseDto,
    UpdateServiceDto,
    ServiceListFilterDto,
    PaginatedResponse,
)
from ..shared.auth import get_admin_user, get_operator_user

service_router = APIRouter(
    prefix="/services", tags=["services"], include_in_schema=True
)


def get_repository():
    return ServiceRepository()


@service_router.get(
    "/",
    response_model=PaginatedResponse[ServiceResponseDto],
    summary="Listar serviços",
    description="Lista todos os serviços com paginação e filtros. Acesso permitido para admin e operator.",
)
async def list_services(
    is_active: bool | None = Query(None),
    name: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _operator_payload: dict = Depends(get_operator_user),
) -> dict:
    """
    Endpoint para listar serviços com paginação e filtros.
    Acesso permitido para admin e operator.
    """
    filter_dto = ServiceListFilterDto(
        is_active=is_active, name=name, page=page, page_size=page_size
    )
    use_case = GetServicesListUsecase(filter_dto, ServiceRepository())
    services, total_count = await use_case.execute()

    return {
        "items": services,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size,
    }


@service_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Criar serviço",
    description="Cria um novo serviço. Acesso restrito a administradores.",
)
async def create_service(
    create_service_dto: CreateServiceDto,
    _admin_payload: dict = Depends(get_admin_user),
) -> ServiceResponseDto:
    """
    Cria um novo serviço.
    Acesso restrito a administradores.
    """
    use_case = CreateServiceUsecase(create_service_dto, ServiceRepository())
    return await use_case.execute()


@service_router.put(
    "/{service_id}",
    response_model=ServiceResponseDto,
    summary="Atualizar serviço",
    description="Atualiza um serviço existente. Acesso restrito a administradores.",
)
async def update_service(
    service_id: str,
    update_service_dto: UpdateServiceDto,
    _admin_payload: dict = Depends(get_admin_user),
) -> ServiceResponseDto:
    """
    Atualiza um serviço.
    Acesso restrito a administradores.
    """
    use_case = UpdateServiceUsecase(service_id, update_service_dto, ServiceRepository())
    return await use_case.execute()


@service_router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar serviço",
    description="Deleta um serviço. Acesso restrito a administradores.",
)
async def delete_service(
    service_id: str,
    _admin_payload: dict = Depends(get_admin_user),
) -> None:
    """
    Apaga um serviço.
    Acesso restrito a administradores.
    """
    use_case = DeleteServiceUsecase(service_id, ServiceRepository())
    await use_case.execute()


@service_router.get(
    "/{service_id}",
    response_model=ServiceResponseDto,
    summary="Obter serviço por ID",
    description="Obtém um serviço pelo seu ID. Acesso permitido para admin e operator.",
)
async def get_service_by_id(
    service_id: str,
    _operator_payload: dict = Depends(get_operator_user),
) -> ServiceResponseDto:
    """
    Obtém um serviço pelo seu ID.
    Acesso permitido para admin e operator.
    """
    use_case = GetServiceByIdUsecase(service_id, ServiceRepository())
    service = await use_case.execute()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
