# tests/controllers/test_user_controller.py
import pytest
from fastapi.testclient import TestClient
from t1_construcao.main import app # Importe a sua app FastAPI

# NOVO: Importe as dependências REAIS que você quer substituir
from t1_construcao.shared.auth import (
    get_admin_user, 
    get_current_user_payload
)

@pytest.fixture
def client():
    """Cliente de teste que limpa os overrides após cada teste."""
    with TestClient(app) as c:
        yield c
    # Limpa os overrides para garantir que os testes não interfiram uns com os outros
    app.dependency_overrides = {}


# --- Payloads Falsos (Mocks) ---
ADMIN_PAYLOAD = {
    "sub": "admin-uuid-12345",
    "cognito:groups": ["admin"],
    "username": "admin-user"
}

USER_PAYLOAD = {
    "sub": "user-uuid-67890",
    "cognito:groups": ["user"],
    "username": "normal-user"
}

# --- Testes de Segurança (RBAC) ---

def test_delete_user_as_admin_success(client, mocker):
    """
    Testa se um admin CONSEGUE apagar um utilizador.
    """
    # 💡 A MÁGICA: Substitua a dependência 'get_admin_user'
    app.dependency_overrides[get_admin_user] = lambda: ADMIN_PAYLOAD
    
    # O mock do use case continua igual
    mocker.patch(
        "t1_construcao.application.usecases.DeleteUserUsecase.execute", 
        return_value=None
    )

    response = client.delete(
        "/users/some-user-id",
        headers={"Authorization": "Bearer fake-admin-token"} 
    )
    
    # Agora a dependência foi satisfeita e o status_code deve ser 204
    assert response.status_code == 204

def test_delete_user_as_normal_user_fails(client, mocker):
    """
    Testa se um utilizador normal NÃO CONSEGUE apagar.
    """
    # 💡 A MÁGICA: A rota 'delete_user' depende de 'get_admin_user',
    # que por sua vez depende de 'get_current_user_payload'.
    # Vamos substituir 'get_current_user_payload' para que devolva um utilizador normal.
    app.dependency_overrides[get_current_user_payload] = lambda: USER_PAYLOAD

    response = client.delete(
        "/users/some-user-id",
        headers={"Authorization": "Bearer fake-user-token"}
    )
    
    # A função real 'get_admin_user' vai executar, receber o USER_PAYLOAD,
    # ver que não tem "admin" e lançar a excepção 403.
    assert response.status_code == 403 
    assert response.json()["detail"] == "Acesso restrito a administradores"

def test_get_own_user_data_success(client, mocker):
    """
    Testa se um utilizador normal CONSEGUE ver os seus próprios dados.
    """
    # 💡 A MÁGICA: A rota depende de 'check_admin_or_self', 
    # que depende de 'get_current_user_payload'. Substituímos este último.
    app.dependency_overrides[get_current_user_payload] = lambda: USER_PAYLOAD
    
    mocker.patch(
        "t1_construcao.application.usecases.GetUserByIdUsecase.execute", 
        return_value={"id": "user-uuid-67890", "name": "normal-user", "email": "..."}
    )

    # O ID na URL ('user-uuid-67890') é o MESMO 'sub' do USER_PAYLOAD
    response = client.get(
        "/users/user-uuid-67890", 
        headers={"Authorization": "Bearer fake-user-token"}
    )
    
    # A função 'check_admin_or_self' vai passar
    assert response.status_code == 200
    assert response.json()["id"] == "user-uuid-67890"

def test_get_other_user_data_as_normal_user_fails(client, mocker):
    """
    Testa se um utilizador normal NÃO CONSEGUE ver dados de outro utilizador.
    """
    app.dependency_overrides[get_current_user_payload] = lambda: USER_PAYLOAD

    # O ID na URL ('another-persons-id') é DIFERENTE do 'sub' do USER_PAYLOAD
    response = client.get(
        "/users/another-persons-id", 
        headers={"Authorization": "Bearer fake-user-token"}
    )
    
    # A função 'check_admin_or_self' vai falhar
    assert response.status_code == 403
    assert response.json()["detail"] == "Acesso permitido apenas para admin ou o próprio utilizador"

def test_get_other_user_data_as_admin_success(client, mocker):
    """
    Testa se um admin CONSEGUE ver os dados de qualquer utilizador.
    """
    # 💡 A MÁGICA: Substituímos o payload para ser de um admin
    app.dependency_overrides[get_current_user_payload] = lambda: ADMIN_PAYLOAD
    
    mocker.patch(
        "t1_construcao.application.usecases.GetUserByIdUsecase.execute", 
        return_value={"id": "user-uuid-67890", "name": "normal-user", "email": "..."}
    )

    # O admin (do payload) está a aceder a um ID de outro utilizador
    response = client.get(
        "/users/user-uuid-67890", 
        headers={"Authorization": "Bearer fake-admin-token"}
    )
    
    # A função 'check_admin_or_self' passa (porque é admin)
    assert response.status_code == 200
    assert response.json()["id"] == "user-uuid-67890"