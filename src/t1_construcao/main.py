from contextlib import asynccontextmanager
from fastapi import FastAPI
from t1_construcao.infrastructure import DatabaseStarterService

db_service = DatabaseStarterService()

@asynccontextmanager
async def lifespan(_: FastAPI):
    await db_service.startup()
    yield
    await db_service.shutdown()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}