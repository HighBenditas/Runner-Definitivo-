from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.objetivo_schema import ObjetivoCreate

from api_gateway.app.core.database import get_db
from api_gateway.app.services.objetivo_service import ObjetivoService


router = APIRouter(
    prefix="/objetivos",
    tags=["Objetivos"]
)


@router.post("/")
async def crear_objetivo(
    data: ObjetivoCreate,
    session: AsyncSession = Depends(get_db)
):

    objetivo_id = await ObjetivoService.crear_objetivo(
        session=session,
        usuario_id=data.usuario_id,
        url_objetivo=data.url_objetivo
    )

    return {
        "message": "objetivo creado",
        "objetivo_id": objetivo_id
    }