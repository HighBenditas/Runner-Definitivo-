from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.models.usuarios import Usuario


class UsuarioRepository:

    @staticmethod
    async def obtener_por_external_id(session: AsyncSession, external_id: str):
        query = select(Usuario).where(Usuario.external_id == external_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def crear(session: AsyncSession, external_id: str):
        # La tabla usuarios tiene columnas NOT NULL sin default (nombre, email,
        # password_hash, rol). Los usuarios creados desde el orquestador son
        # tenants (identidad real en Firebase, no se loguean en el runner): por
        # eso nombre/email se derivan del external_id y password_hash es un
        # placeholder no utilizable. `id` es IDENTITY (autogenerado).
        query = (
            insert(Usuario)
            .values(
                external_id=external_id,
                nombre=f"tenant:{external_id}",
                email=f"{external_id}@tenant.dani-eth.local",
                password_hash="!external-auth-no-login",
                rol="tenant",
            )
            .returning(Usuario.id)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalar()
