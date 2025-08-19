from tortoise import fields
from tortoise.models import Model


__all__ = ["User"]


class User(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)

    class Meta:
        table = "users"