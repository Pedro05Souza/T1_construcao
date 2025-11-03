import os
import requests
from jose import jwk, jwt
from fastapi import HTTPException, Security, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

try:
    COGNITO_ISSUER = os.environ["JWT_ISSUER"]
    COGNITO_AUDIENCE = os.environ["JWT_AUDIENCE"]
    JWKS_URI = f"{COGNITO_ISSUER}/.well-known/jwks.json"
except KeyError as e:
    raise RuntimeError(f"Variável de ambiente {e} não definida. Verifique o seu ficheiro .env") from e


try:
    jwks_response = requests.get(JWKS_URI, timeout=10)
    jwks_response.raise_for_status()
    jwks = jwks_response.json()["keys"]
except requests.exceptions.RequestException as e:
    print(f"ERRO CRÍTICO: Não foi possível buscar o JWKS em {JWKS_URI}. {e}")
    jwks = []

security_scheme = HTTPBearer(
    description="Insira o Access Token (JWT) fornecido pelo Cognito/Auth0."
)


def validate_token(token: str) -> dict:
    """Valida o token JWT (assinatura, claims) usando o JWKS do Cognito."""
    if not jwks:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="JWKS não disponível, validação falhou")
        
    try:
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]
    except Exception as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Cabeçalho do token inválido") from e

    key = next((k for k in jwks if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Chave pública (JWKS) não encontrada para o kid")

    try:
        public_key = jwk.construct(key)
        
        payload = jwt.decode(
            token,
            public_key.to_pem(),
            algorithms=["RS256"],
            issuer=COGNITO_ISSUER,
            audience=COGNITO_AUDIENCE
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expirado") from e
    except jwt.JWTClaimsError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"Claims inválidas: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"Erro desconhecido na validação do token: {e}") from e

def get_current_user_payload(creds: HTTPAuthorizationCredentials = Security(security_scheme)) -> dict:
    """
    Dependência básica: Valida o token e retorna o payload (claims).
    Qualquer rota que usar isto exigirá um token válido.
    """
    token = creds.credentials
    payload = validate_token(token)
    return payload

def get_admin_user(payload: dict = Depends(get_current_user_payload)) -> dict:
    """
    Dependência de Admin: Exige um token válido E que o usuário
    esteja no grupo 'admin'.
    """
    groups = payload.get("cognito:groups", [])
    if "admin" not in groups:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="Acesso restrito a administradores"
        )
    return payload

def check_admin_or_self(
    user_id: str = Path(..., description="ID do usuário a ser acedido"), 
    payload: dict = Depends(get_current_user_payload)
) -> dict:
    """
    Dependência de Autorização (RBAC):
    Verifica se o utilizador é 'admin' OU se é o próprio utilizador (self).
    Compara o 'sub' (ID do utilizador no token) com o 'user_id' da URL.
    """
    user_groups = payload.get("cognito:groups", [])
    
    user_sub_id = payload.get("sub") 

    if "admin" in user_groups or user_sub_id == user_id:
        return payload
    
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, 
        detail="Acesso permitido apenas para admin ou o próprio utilizador"
    )