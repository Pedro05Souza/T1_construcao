from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from t1_construcao.infrastructure import DatabaseStarterService
from t1_construcao.controllers.user_controller import user_router
from t1_construcao.controllers.service_controller import service_router
from t1_construcao.controllers.appointment_controller import appointment_router

db_service = DatabaseStarterService()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db_service.startup()
    yield
    await db_service.shutdown()


app = FastAPI(
    lifespan=lifespan,
    title="Construção de Software API",
    description="""
    API REST para gestão de agendamentos de serviços.
    
    ## Funcionalidades
    
    * **Usuários**: Gestão de usuários com papéis (admin, operator, client)
    * **Serviços**: CRUD de serviços disponíveis
    * **Agendamentos**: Sistema completo de agendamentos com fluxos de negócio
    
    ## Autenticação
    
    Todas as rotas (exceto `/`) requerem autenticação via JWT Bearer Token.
    O token deve ser obtido do AWS Cognito e incluído no header:
    
    ```
    Authorization: Bearer <token>
    ```
    
    ## Papéis e Permissões
    
    * **admin**: Acesso total a todas as funcionalidades
    * **operator**: Pode gerenciar serviços e agendamentos, confirmar agendamentos
    * **client**: Pode criar e gerenciar seus próprios agendamentos
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def custom_openapi():
    """
    Esta função personaliza o schema OpenAPI para incluir
    a autenticação Bearer (JWT) e melhorar a documentação.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Adicionar informações de contato e licença
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
    }
    openapi_schema["info"]["license"] = {
        "name": "MIT",
    }

    # Configurar esquemas de segurança
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Insira o Access Token (JWT) obtido do AWS Cognito. O token deve ser válido e incluir os claims: iss, aud, exp, nbf.",
        }
    }

    security_requirement = [{"bearerAuth": []}]

    # Aplicar segurança a todas as rotas exceto as públicas
    public_paths = ["/docs", "/openapi.json", "/redoc", "/"]

    for path, path_item in openapi_schema.get("paths", {}).items():
        for method in path_item:
            if path not in public_paths:
                path_item[method]["security"] = security_requirement

                # Adicionar tags para melhor organização
                if "tags" not in path_item[method]:
                    # Extrair tag do path
                    if path.startswith("/api/v1/users"):
                        path_item[method]["tags"] = ["users"]
                    elif path.startswith("/api/v1/services"):
                        path_item[method]["tags"] = ["services"]
                    elif path.startswith("/api/v1/appointments"):
                        path_item[method]["tags"] = ["appointments"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# API v1 routes
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(user_router)
api_v1_router.include_router(service_router)
api_v1_router.include_router(appointment_router)

app.include_router(api_v1_router)

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
