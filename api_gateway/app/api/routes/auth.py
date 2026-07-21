import os
import httpx

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from shared.schemas.usuario_schema import (
    UsuarioRegister,
    UsuarioLogin
)

from api_gateway.app.core.database import get_db
from api_gateway.app.services.usuario_service import UsuarioService



router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)



SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")



@router.post("/register")
async def register(
    data: UsuarioRegister,
    session: AsyncSession = Depends(get_db)
):


    url = f"{SUPABASE_URL}/auth/v1/signup"


    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type":"application/json"
    }


    payload = {
        "email":data.email,
        "password":data.password
    }


    async with httpx.AsyncClient() as client:

        response = await client.post(
            url,
            headers=headers,
            json=payload
        )


    if response.status_code not in (200,201):

        raise HTTPException(
            status_code=400,
            detail=response.text
        )


    supabase_response=response.json()
    print("RESPUESTA SUPABASE:", supabase_response)

    user=supabase_response.get("user")


    if not user:

        raise HTTPException(
            status_code=400,
            detail="Supabase no devolvió usuario"
        )


    external_id=user["id"]



    usuario_id = await UsuarioService.obtener_o_crear(
        session=session,
        nombre=data.nombre,
        email=data.email,
        rol=data.rol,
        external_id=external_id
    )


    return {

        "message":"Usuario creado correctamente",

        "usuario_id":usuario_id,

        "external_id":external_id

    }

@router.post("/login")
async def login(
    data: UsuarioLogin
):
    
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "email": data.email,
        "password": data.password
    }


    async with httpx.AsyncClient() as client:

        response = await client.post(
            url,
            headers=headers,
            json=payload
        )


    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=response.text
        )


    supabase_response = response.json()


    return {
        "message": "Login correcto",
        "access_token": supabase_response["access_token"],
        "refresh_token": supabase_response["refresh_token"],
        "user": supabase_response["user"]
    }