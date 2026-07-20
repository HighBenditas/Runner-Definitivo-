from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.models.sesiones_escaneo import SesionEscaneo


class SesionRepository:

    @staticmethod
    async def crear_sesion(
        session: AsyncSession,
        objetivo_id: int
    ):

        query = (
            insert(SesionEscaneo)
            .values(
                objetivo_id=objetivo_id,
                estado="pendiente"
            )
            .returning(SesionEscaneo.id)
        )

        result = await session.execute(query)

        await session.commit()

        sesion_id = result.scalar()

        return sesion_id