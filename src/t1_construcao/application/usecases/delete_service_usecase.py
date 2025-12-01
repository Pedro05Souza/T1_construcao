from t1_construcao.domain import ServiceRepository

__all__ = ["DeleteServiceUsecase"]


class DeleteServiceUsecase:

    def __init__(self, service_id: str, service_repository: ServiceRepository):
        self._service_id = service_id
        self._service_repository = service_repository

    async def execute(self) -> None:
        await self._service_repository.delete(self._service_id)
