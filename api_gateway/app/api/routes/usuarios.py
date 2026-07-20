from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.usuario_schema import UsuarioCreate

from api_gateway.app.core.database import get_db
from api_gateway.app.services.usuario_service import UsuarioService


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post("/")
async def crear_usuario(
    data: UsuarioCreate,
    session: AsyncSession = Depends(get_db)
):
    """Get-or-create de un usuario por su external_id (uid de Firebase)."""
    usuario_id = await UsuarioService.obtener_o_crear(
        session=session,
        external_id=data.external_id
    )

    return {
        "message": "usuario resuelto",
        "usuario_id": usuario_id
    }
