from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.models.objetivos import Objetivo


class ObjetivoRepository:

    @staticmethod
    async def crear_objetivo(
        session: AsyncSession,
        usuario_id: int,
        url_objetivo: str
    ):

        query = (
            insert(Objetivo)
            .values(
                usuario_id=usuario_id,
                url_objetivo=url_objetivo
            )
            .returning(Objetivo.id)
        )

        result = await session.execute(query)

        await session.commit()

        objetivo_id = result.scalar()

        return objetivo_id