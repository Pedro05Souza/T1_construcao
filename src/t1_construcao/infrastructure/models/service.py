from tortoise import fields
from tortoise.models import Model


__all__ = ["Service"]


class Service(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    duration_minutes = fields.IntField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "services"
