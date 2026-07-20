from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.app.repositories.sesion_repository import SesionRepository


class SesionService:

    @staticmethod
    async def crear_sesion(
        session: AsyncSession,
        objetivo_id: int
    ):

        sesion_id = await SesionRepository.crear_sesion(
            session=session,
            objetivo_id=objetivo_id
        )

        return sesion_id