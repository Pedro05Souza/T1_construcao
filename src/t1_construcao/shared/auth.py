import os
import requests
from jose import jwk, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from fastapi import HTTPException, Security, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

try:
    COGNITO_ISSUER = os.environ["JWT_ISSUER"]
    COGNITO_AUDIENCE = os.environ["JWT_AUDIENCE"]
    JWKS_URI = f"{COGNITO_ISSUER}/.well-known/jwks.json"
except KeyError as e:
    raise RuntimeError(
        f"Variável de ambiente {e} não definida. Verifique a .env"
    ) from e


try:
    jwks_response = requests.get(JWKS_URI, timeout=10)
    jwks_response.raise_for_status()
    jwks = jwks_response.json()["keys"]
except requests.exceptions.RequestException as e:
    jwks = []

security_scheme = HTTPBearer(
    description="Insira o Access Token (JWT) fornecido pelo Cognito/Auth0."
)


def validate_token(token: str) -> dict:
    if not jwks:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="JWKS não disponível, validação falhou",
        )

    try:
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Cabeçalho do token inválido"
        ) from e

    key = next((k for k in jwks if k["kid"] == kid), None)
    if not key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Chave pública (JWKS) não encontrada para o kid",
        )

    try:
        public_key = jwk.construct(key)

        payload = jwt.decode(
            token,
            public_key.to_pem(),
            algorithms=["RS256"],
            issuer=COGNITO_ISSUER,
            audience=COGNITO_AUDIENCE,
            options={
                "verify_signature": True,
                "verify_iss": True,
                "verify_aud": True,
                "verify_exp": True,
                "verify_nbf": True,
            },
        )
        return payload
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Token expirado"
        ) from e
    except JWTClaimsError as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=f"Claims inválidas: {e}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Erro desconhecido na validação do token: {e}",
        ) from e


def get_current_user_payload(
    creds: HTTPAuthorizationCredentials = Security(security_scheme),
) -> dict:
    """
    Dependência básica: Valida o token e retorna o payload (claims).
    Qualquer rota que usar isto exigirá um token válido.
    """
    token = creds.credentials
    payload = validate_token(token)
    return payload


def get_admin_user(payload: dict = Depends(get_current_user_payload)) -> dict:
    """
    Dependência de Admin: Exige um token válido e que o usuário
    esteja no grupo 'admin'.
    """
    groups = payload.get("cognito:groups", [])
    if "admin" not in groups:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores"
        )
    return payload


def get_operator_user(payload: dict = Depends(get_current_user_payload)) -> dict:
    """
    Dependência de Operator: Exige um token válido e que o usuário
    esteja no grupo 'admin' ou 'operator'.
    """
    groups = payload.get("cognito:groups", [])
    if "admin" not in groups and "operator" not in groups:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores ou operadores",
        )
    return payload


def get_client_user(payload: dict = Depends(get_current_user_payload)) -> dict:
    """
    Dependência de Client: Exige um token válido e que o usuário
    esteja no grupo 'admin', 'operator' ou 'client'.
    """
    groups = payload.get("cognito:groups", [])
    if "admin" not in groups and "operator" not in groups and "client" not in groups:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Acesso restrito a usuários autenticados",
        )
    return payload


def check_admin_or_self(
    user_id: str = Path(..., description="ID do usuário a ser acedido"),
    payload: dict = Depends(get_current_user_payload),
) -> dict:
    """
    Dependência de Autorização (RBAC):
    Verifica se o user é 'admin' ou se é o próprio user (self).
    Compara o 'sub' (ID do user no token) com o 'user_id' da URL.
    """
    user_groups = payload.get("cognito:groups", [])

    user_sub_id = payload.get("sub")

    if "admin" in user_groups or user_sub_id == user_id:
        return payload

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Acesso permitido apenas para admin ou o próprio user",
    )


def check_appointment_ownership(
    appointment_id: str = Path(..., description="ID do agendamento a ser acedido"),
    payload: dict = Depends(get_current_user_payload),
) -> dict:
    """
    Dependência de Autorização (RBAC + Ownership):
    Verifica se o user é 'admin', 'operator' ou se é o dono do agendamento.
    """
    user_groups = payload.get("cognito:groups", [])
    user_sub_id = payload.get("sub")

    # Admin e operator têm acesso total
    if "admin" in user_groups or "operator" in user_groups:
        return payload

    # Para client, verificar ownership será feito no controller
    # retornando o payload para uso posterior
    return payload
