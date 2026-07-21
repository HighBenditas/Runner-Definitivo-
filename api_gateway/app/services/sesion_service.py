from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.app.repositories.sesion_repository import SesionRepository
from shared.database.models.objetivos import Objetivo


class SesionService:

    @staticmethod
    async def crear_sesion(
        session: AsyncSession,
        id_usuario: int | None = None,
        objetivo_id: int | None = None
    ):

        if id_usuario is None:
            if objetivo_id is None:
                raise ValueError("Se requiere id_usuario u objetivo_id")

            result = await session.execute(
                select(Objetivo.usuario_id).where(Objetivo.id == objetivo_id)
            )

            id_usuario = result.scalar()

            if id_usuario is None:
                raise ValueError("No se encontró el usuario asociado al objetivo")

        sesion_id = await SesionRepository.crear_sesion(
            session=session,
            id_usuario=id_usuario
        )

        return sesion_id