from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.objetivo_schema import ObjetivoCreate

from api_gateway.app.core.database import get_db
from api_gateway.app.services.objetivo_service import ObjetivoService

from shared.auth import verificar_usuario
from shared.internal_auth import verificar_token_interno



router = APIRouter(
    prefix="/objetivos",
    tags=["Objetivos"],
    dependencies=[
        Depends(verificar_token_interno),
        Depends(verificar_usuario)
    ]
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