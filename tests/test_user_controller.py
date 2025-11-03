import pytest
from fastapi.testclient import TestClient
from t1_construcao.main import app

from t1_construcao.shared.auth import (
    get_admin_user, 
    get_current_user_payload
)

@pytest.fixture
def test_client():
    """Cliente de teste que limpa os overrides após cada teste."""
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}

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

def test_delete_user_as_admin_success(test_client, mocker):
    """
    Testa se um admin CONSEGUE apagar um utilizador.
    """
    app.dependency_overrides[get_admin_user] = lambda: ADMIN_PAYLOAD
    
    mocker.patch(
        "t1_construcao.application.usecases.DeleteUserUsecase.execute", 
        return_value=None
    )

    response = test_client.delete(
        "/users/some-user-id",
        headers={"Authorization": "Bearer fake-admin-token"} 
    )
    
    assert response.status_code == 204

def test_delete_user_as_normal_user_fails(test_client):
    """
    Testa se um utilizador normal NÃO CONSEGUE apagar.
    """
    app.dependency_overrides[get_current_user_payload] = lambda: USER_PAYLOAD

    response = test_client.delete(
        "/users/some-user-id",
        headers={"Authorization": "Bearer fake-user-token"}
    )
    
    assert response.status_code == 403 
    assert response.json()["detail"] == "Acesso restrito a administradores"

def test_get_own_user_data_success(test_client, mocker):
    """
    Testa se um utilizador normal CONSEGUE ver os seus próprios dados.
    """
    app.dependency_overrides[get_current_user_payload] = lambda: USER_PAYLOAD
    
    mocker.patch(
        "t1_construcao.application.usecases.GetUserByIdUsecase.execute", 
        return_value={"id": "user-uuid-67890", "name": "normal-user", "email": "..."}
    )

    response = test_client.get(
        "/users/user-uuid-67890", 
        headers={"Authorization": "Bearer fake-user-token"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == "user-uuid-67890"

def test_get_other_user_data_as_normal_user_fails(test_client):
    """
    Testa se um utilizador normal NÃO CONSEGUE ver dados de outro utilizador.
    """
    app.dependency_overrides[get_current_user_payload] = lambda: USER_PAYLOAD

    response = test_client.get(
        "/users/another-persons-id", 
        headers={"Authorization": "Bearer fake-user-token"}
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Acesso permitido apenas para admin ou o próprio utilizador"

def test_get_other_user_data_as_admin_success(test_client, mocker):
    """
    Testa se um admin CONSEGUE ver os dados de qualquer utilizador.
    """
    app.dependency_overrides[get_current_user_payload] = lambda: ADMIN_PAYLOAD
    
    mocker.patch(
        "t1_construcao.application.usecases.GetUserByIdUsecase.execute", 
        return_value={"id": "user-uuid-67890", "name": "normal-user", "email": "..."}
    )

    response = test_client.get(
        "/users/user-uuid-67890", 
        headers={"Authorization": "Bearer fake-admin-token"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == "user-uuid-67890"