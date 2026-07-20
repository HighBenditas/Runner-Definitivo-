from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.sesion_schema import SesionCreate

from api_gateway.app.core.database import get_db
from api_gateway.app.services.sesion_service import SesionService


router = APIRouter(
    prefix="/sesiones",
    tags=["Sesiones"]
)


@router.post("/")
async def crear_sesion(
    data: SesionCreate,
    session: AsyncSession = Depends(get_db)
):

    sesion_id = await SesionService.crear_sesion(
        session=session,
        objetivo_id=data.objetivo_id
    )

    return {
        "message": "sesion creada",
        "sesion_id": sesion_id
    }