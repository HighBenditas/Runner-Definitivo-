import jwt

from jwt import PyJWKClient

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


SUPABASE_JWKS_URL = (
    "https://ucsspxcvdqlirvhxuzce.supabase.co/"
    "auth/v1/.well-known/jwks.json"
)


security = HTTPBearer(
    scheme_name="Bearer Authentication",
    description="Ingrese el JWT de Supabase con formato: Bearer token"
)


jwks_client = PyJWKClient(
    SUPABASE_JWKS_URL
)


async def verificar_usuario(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials


    try:

        signing_key = jwks_client.get_signing_key_from_jwt(
            token
        )


        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated"
        )


        print("JWT VALIDADO:", payload)


        return payload


    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="JWT expirado"
        )


    except Exception as e:

        print("ERROR JWT:", e)

        raise HTTPException(
            status_code=401,
            detail=f"JWT inválido: {str(e)}"
        )