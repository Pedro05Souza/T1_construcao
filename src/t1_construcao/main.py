from contextlib import asynccontextmanager
from fastapi import FastAPI
from t1_construcao.infrastructure import DatabaseStarterService
from t1_construcao.controllers.user_controller import user_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

db_service = DatabaseStarterService()

@asynccontextmanager
async def lifespan(_: FastAPI):
    await db_service.startup()
    yield
    await db_service.shutdown()


app = FastAPI(
    lifespan=lifespan,
    title="Construção de Software API",
    description="API para gestão de utilizadores com Cognito",
    version="1.0.0"
)
def custom_openapi():
    """
    Esta função personaliza o schema OpenAPI para incluir
    a autenticação Bearer (JWT).
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Insira o Access Token (JWT) obtido do Cognito"
        }
    }

    security_requirement = [{"bearerAuth": []}]
    
    for path, path_item in openapi_schema.get("paths", {}).items():
        for method in path_item:
            if path not in ["/docs", "/openapi.json", "/redoc", "/"]:
                 path_item[method]["security"] = security_requirement

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.include_router(user_router)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://t1-app-construcao-seu-nome-123.auth.us-east-1.amazoncognito.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
