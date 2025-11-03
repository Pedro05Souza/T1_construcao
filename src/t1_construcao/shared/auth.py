# src/t1_construcao/shared/auth.py

import os
import requests
from jose import jwk, jwt
from jose.utils import base64url_decode
from fastapi import HTTPException, Security, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

# --- Configuração (Virá do .env) ---
# Certifique-se de que estas variáveis de ambiente estão definidas
try:
    COGNITO_ISSUER = os.environ["JWT_ISSUER"]
    COGNITO_AUDIENCE = os.environ["JWT_AUDIENCE"] # O seu App Client ID
    JWKS_URI = f"{COGNITO_ISSUER}/.well-known/jwks.json"
except KeyError as e:
    raise RuntimeError(f"Variável de ambiente {e} não definida. Verifique o seu ficheiro .env")


# --- Cache do JWKS ---
# Em produção, isto deve ter um TTL (cache com tempo de expiração)
# Para a atividade, baixar uma vez no arranque é suficiente.
try:
    jwks_response = requests.get(JWKS_URI)
    jwks_response.raise_for_status() # Lança erro se o request falhar
    jwks = jwks_response.json()["keys"]
except requests.exceptions.RequestException as e:
    print(f"ERRO CRÍTICO: Não foi possível buscar o JWKS em {JWKS_URI}. {e}")
    jwks = [] # A app vai falhar a validação de todos os tokens


# --- Esquema de Segurança ---
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
    except Exception:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Cabeçalho do token inválido")

    # Encontra a chave pública correta no JWKS
    key = next((k for k in jwks if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Chave pública (JWKS) não encontrada para o kid")

    try:
        # Constrói a chave pública RSA
        public_key = jwk.construct(key)
        
        # Decodifica e VALIDA a assinatura e as claims
        payload = jwt.decode(
            token,
            public_key.to_pem(),
            algorithms=["RS260"], # Algoritmo usado pelo Cognito
            issuer=COGNITO_ISSUER,
            audience=COGNITO_AUDIENCE # Valida o 'aud' (App Client ID)
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.JWTClaimsError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"Claims inválidas: {e}")
    except Exception as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"Erro desconhecido na validação do token: {e}")

# --- Dependências do FastAPI (para injetar nas rotas) ---

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
    
    # 'sub' é o ID universal único do utilizador dentro do Cognito User Pool
    user_sub_id = payload.get("sub") 

    # Permite se for admin OU se o ID do token for o mesmo da URL
    if "admin" in user_groups or user_sub_id == user_id:
        return payload
    
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, 
        detail="Acesso permitido apenas para admin ou o próprio utilizador"
    )