from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.sesion_schema import SesionCreate

from api_gateway.app.core.database import get_db
from api_gateway.app.services.sesion_service import SesionService

from shared.auth import verificar_usuario
from shared.internal_auth import verificar_token_interno


router = APIRouter(
    prefix="/sesiones",
    tags=["Sesiones"],
    dependencies=[
        Depends(verificar_token_interno),
        Depends(verificar_usuario)
    ]
)


@router.post("/")
async def crear_sesion(
    data: SesionCreate,
    session: AsyncSession = Depends(get_db)
):
    try:
        sesion_id = await SesionService.crear_sesion(
            session=session,
            id_usuario=data.id_usuario,
            objetivo_id=data.objetivo_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "sesion creada",
        "sesion_id": sesion_id
    }