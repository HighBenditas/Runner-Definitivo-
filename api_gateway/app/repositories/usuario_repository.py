from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database.models.usuarios import Usuario


class UsuarioRepository:


    @staticmethod
    async def obtener_por_external_id(
        session: AsyncSession,
        external_id: str
    ):

        resultado = await session.execute(
            select(Usuario)
            .where(Usuario.external_id == external_id)
        )

        return resultado.scalar_one_or_none()



    @staticmethod
    async def crear(
        session: AsyncSession,
        nombre: str,
        email: str,
        rol: str,
        external_id: str
    ):

        usuario = Usuario(
            nombre=nombre,
            email=email,
            password_hash="SUPABASE_AUTH",
            rol=rol,
            external_id=external_id
        )


        session.add(usuario)

        await session.commit()

        await session.refresh(usuario)

        return usuario