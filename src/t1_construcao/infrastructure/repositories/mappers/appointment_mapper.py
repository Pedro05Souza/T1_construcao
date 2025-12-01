from t1_construcao.infrastructure.models.appointment import Appointment
from t1_construcao.domain.entities.appointment_entity import AppointmentEntity


def appointment_model_to_entity(appointment_model: Appointment) -> AppointmentEntity:
    return AppointmentEntity(
        id=str(appointment_model.id),
        user_id=str(appointment_model.user_id),
        service_id=str(appointment_model.service_id),
        scheduled_at=appointment_model.scheduled_at,
        status=appointment_model.status,
        notes=appointment_model.notes,
        created_at=appointment_model.created_at,
        updated_at=appointment_model.updated_at,
    )
