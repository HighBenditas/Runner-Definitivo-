from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.usuario_schema import UsuarioCreate

from api_gateway.app.core.database import get_db
from api_gateway.app.services.usuario_service import UsuarioService

from shared.auth import verificar_usuario
from shared.internal_auth import verificar_token_interno



router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[
        Depends(verificar_token_interno),
        Depends(verificar_usuario)
    ]
)



@router.post("/")
async def crear_usuario(
    data: UsuarioCreate,
    session: AsyncSession = Depends(get_db)
):

    usuario_id = await UsuarioService.obtener_o_crear(
        session=session,
        nombre=data.nombre,
        email=data.email,
        rol=data.rol,
        external_id=data.external_id
    )

    return {
        "message": "usuario creado",
        "usuario_id": usuario_id
    }