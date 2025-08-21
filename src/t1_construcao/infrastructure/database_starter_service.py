from tortoise import Tortoise
from ._tortoise_config import TORTOISE_ORM

__all__ = ["DatabaseStarterService"]


class DatabaseStarterService:

    def __init__(self) -> None:
        pass

    async def startup(self) -> None:
        """Initialize database connection and generate schemas"""
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()

    async def shutdown(self) -> None:
        """Close database connections"""
        await Tortoise.close_connections()
