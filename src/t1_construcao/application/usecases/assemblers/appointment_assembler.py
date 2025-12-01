from t1_construcao.application.dtos import AppointmentResponseDto
from t1_construcao.domain.entities import AppointmentEntity

__all__ = ["to_appointment_dto"]


def to_appointment_dto(appointment_entity: AppointmentEntity) -> AppointmentResponseDto:
    return AppointmentResponseDto(
        id=appointment_entity.id,
        user_id=appointment_entity.user_id,
        service_id=appointment_entity.service_id,
        scheduled_at=appointment_entity.scheduled_at,
        status=appointment_entity.status,
        notes=appointment_entity.notes,
        created_at=appointment_entity.created_at,
        updated_at=appointment_entity.updated_at,
    )
