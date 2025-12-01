from tortoise import fields
from tortoise.models import Model
from .user import User
from .service import Service


__all__ = ["Appointment"]


class Appointment(Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="appointments")
    service = fields.ForeignKeyField("models.Service", related_name="appointments")
    scheduled_at = fields.DatetimeField()
    status = fields.CharField(
        max_length=50, default="pending"
    )  # pending, confirmed, cancelled, completed
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "appointments"
