from contextlib import asynccontextmanager
from fastapi import FastAPI
from t1_construcao.infrastructure import DatabaseStarterService
from t1_construcao.controllers.user_controller import user_router

db_service = DatabaseStarterService()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db_service.startup()
    yield
    await db_service.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
