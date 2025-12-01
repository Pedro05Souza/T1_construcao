from fastapi import APIRouter, status, Depends, HTTPException, Query
from starlette.status import HTTP_403_FORBIDDEN
from datetime import datetime
from t1_construcao.application.usecases import (
    CreateAppointmentUsecase,
    UpdateAppointmentUsecase,
    GetAppointmentByIdUsecase,
    GetAppointmentsListUsecase,
    DeleteAppointmentUsecase,
    ConfirmAppointmentUsecase,
    CancelAppointmentUsecase,
)
from t1_construcao.infrastructure import AppointmentRepository, ServiceRepository
from t1_construcao.application.dtos import (
    CreateAppointmentDto,
    AppointmentResponseDto,
    UpdateAppointmentDto,
    AppointmentListFilterDto,
    ConfirmAppointmentDto,
    CancelAppointmentDto,
    PaginatedResponse,
)
from ..shared.auth import (
    get_admin_user,
    get_operator_user,
    get_client_user,
    check_appointment_ownership,
    get_current_user_payload,
)

appointment_router = APIRouter(
    prefix="/appointments", tags=["appointments"], include_in_schema=True
)


def get_appointment_repository():
    return AppointmentRepository()


def get_service_repository():
    return ServiceRepository()


@appointment_router.get(
    "/",
    response_model=PaginatedResponse[AppointmentResponseDto],
    summary="Listar agendamentos",
    description="Lista agendamentos com paginação e filtros. Admin e operator veem todos; client vê apenas os seus próprios.",
)
async def list_appointments(
    user_id: str | None = Query(None),
    service_id: str | None = Query(None),
    status: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    payload: dict = Depends(get_current_user_payload),
) -> dict:
    """
    Endpoint para listar agendamentos com paginação e filtros.
    - Admin e operator: podem ver todos
    - Client: só vê os seus próprios agendamentos
    """
    groups = payload.get("cognito:groups", [])
    user_sub_id = payload.get("sub")

    # Se for client, forçar filtro por user_id
    if "admin" not in groups and "operator" not in groups:
        user_id = user_sub_id

    filter_dto = AppointmentListFilterDto(
        user_id=user_id,
        service_id=service_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    use_case = GetAppointmentsListUsecase(filter_dto, AppointmentRepository())
    appointments, total_count = await use_case.execute()

    return {
        "items": appointments,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size,
    }


@appointment_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Criar agendamento",
    description="Cria um novo agendamento. O agendamento será criado para o usuário autenticado. Valida conflitos de horário.",
)
async def create_appointment(
    create_appointment_dto: CreateAppointmentDto,
    payload: dict = Depends(get_client_user),
) -> AppointmentResponseDto:
    """
    Cria um novo agendamento.
    Acesso permitido para client, operator e admin.
    O agendamento será criado para o usuário autenticado.
    """
    user_id = payload.get("sub")
    use_case = CreateAppointmentUsecase(
        user_id=user_id,
        create_appointment_dto=create_appointment_dto,
        appointment_repository=AppointmentRepository(),
        service_repository=ServiceRepository(),
    )
    return await use_case.execute()


@appointment_router.put(
    "/{appointment_id}",
    response_model=AppointmentResponseDto,
    summary="Atualizar agendamento",
    description="Atualiza um agendamento existente. Admin e operator podem atualizar qualquer agendamento; client só pode atualizar os seus próprios.",
)
async def update_appointment(
    appointment_id: str,
    update_appointment_dto: UpdateAppointmentDto,
    payload: dict = Depends(check_appointment_ownership),
) -> AppointmentResponseDto:
    """
    Atualiza um agendamento.
    - Admin e operator: podem atualizar qualquer agendamento
    - Client: só pode atualizar os seus próprios agendamentos
    """
    groups = payload.get("cognito:groups", [])
    user_sub_id = payload.get("sub")

    # Verificar ownership se for client
    if "admin" not in groups and "operator" not in groups:
        appointment = await GetAppointmentByIdUsecase(
            appointment_id, AppointmentRepository()
        ).execute()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.user_id != user_sub_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only update your own appointments",
            )

    use_case = UpdateAppointmentUsecase(
        appointment_id=appointment_id,
        update_appointment_dto=update_appointment_dto,
        appointment_repository=AppointmentRepository(),
        service_repository=ServiceRepository(),
    )
    return await use_case.execute()


@appointment_router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar agendamento",
    description="Deleta um agendamento. Admin e operator podem deletar qualquer agendamento; client só pode deletar os seus próprios.",
)
async def delete_appointment(
    appointment_id: str,
    payload: dict = Depends(check_appointment_ownership),
) -> None:
    """
    Apaga um agendamento.
    - Admin e operator: podem apagar qualquer agendamento
    - Client: só pode apagar os seus próprios agendamentos
    """
    groups = payload.get("cognito:groups", [])
    user_sub_id = payload.get("sub")

    # Verificar ownership se for client
    if "admin" not in groups and "operator" not in groups:
        appointment = await GetAppointmentByIdUsecase(
            appointment_id, AppointmentRepository()
        ).execute()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.user_id != user_sub_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only delete your own appointments",
            )

    use_case = DeleteAppointmentUsecase(appointment_id, AppointmentRepository())
    await use_case.execute()


@appointment_router.get(
    "/{appointment_id}",
    response_model=AppointmentResponseDto,
    summary="Obter agendamento por ID",
    description="Obtém um agendamento pelo seu ID. Admin e operator podem ver qualquer agendamento; client só pode ver os seus próprios.",
)
async def get_appointment_by_id(
    appointment_id: str,
    payload: dict = Depends(check_appointment_ownership),
) -> AppointmentResponseDto:
    """
    Obtém um agendamento pelo seu ID.
    - Admin e operator: podem ver qualquer agendamento
    - Client: só pode ver os seus próprios agendamentos
    """
    groups = payload.get("cognito:groups", [])
    user_sub_id = payload.get("sub")

    use_case = GetAppointmentByIdUsecase(appointment_id, AppointmentRepository())
    appointment = await use_case.execute()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Verificar ownership se for client
    if "admin" not in groups and "operator" not in groups:
        if appointment.user_id != user_sub_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only view your own appointments",
            )

    return appointment


@appointment_router.post(
    "/{appointment_id}/confirm",
    response_model=AppointmentResponseDto,
    summary="Confirmar agendamento",
    description="Confirma um agendamento pendente. Acesso permitido apenas para admin e operator.",
)
async def confirm_appointment(
    appointment_id: str,
    confirm_dto: ConfirmAppointmentDto,
    payload: dict = Depends(get_operator_user),
) -> AppointmentResponseDto:
    """
    Confirma um agendamento.
    Acesso permitido para admin e operator.
    """
    use_case = ConfirmAppointmentUsecase(appointment_id, AppointmentRepository())
    return await use_case.execute()


@appointment_router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponseDto,
    summary="Cancelar agendamento",
    description="Cancela um agendamento. Admin e operator podem cancelar qualquer agendamento; client só pode cancelar os seus próprios.",
)
async def cancel_appointment(
    appointment_id: str,
    cancel_dto: CancelAppointmentDto,
    payload: dict = Depends(check_appointment_ownership),
) -> AppointmentResponseDto:
    """
    Cancela um agendamento.
    - Admin e operator: podem cancelar qualquer agendamento
    - Client: só pode cancelar os seus próprios agendamentos
    """
    groups = payload.get("cognito:groups", [])
    user_sub_id = payload.get("sub")

    # Verificar ownership se for client
    if "admin" not in groups and "operator" not in groups:
        appointment = await GetAppointmentByIdUsecase(
            appointment_id, AppointmentRepository()
        ).execute()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.user_id != user_sub_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only cancel your own appointments",
            )

    use_case = CancelAppointmentUsecase(
        appointment_id=appointment_id,
        cancel_appointment_dto=cancel_dto,
        appointment_repository=AppointmentRepository(),
    )
    return await use_case.execute()
