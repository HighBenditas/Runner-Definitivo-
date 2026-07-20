from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.app.repositories.objetivo_repository import ObjetivoRepository


class ObjetivoService:

    @staticmethod
    async def crear_objetivo(
        session: AsyncSession,
        usuario_id: int,
        url_objetivo: str
    ):
        objetivo_id = await ObjetivoRepository.crear_objetivo(
            session=session,
            usuario_id=usuario_id,
            url_objetivo=url_objetivo
        )

        return objetivo_id