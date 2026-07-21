from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api_gateway.app.repositories.usuario_repository import UsuarioRepository


class UsuarioService:

    @staticmethod
    async def obtener_o_crear(
        session: AsyncSession,
        nombre: str,
        email: str,
        rol: str,
        external_id: str
    ):

        usuario = await UsuarioRepository.obtener_por_external_id(
            session,
            external_id
        )

        if usuario:
            return usuario.id

        try:

            usuario = await UsuarioRepository.crear(
                session=session,
                nombre=nombre,
                email=email,
                rol=rol,
                external_id=external_id
            )

            return usuario.id


        except IntegrityError:

            await session.rollback()

            usuario = await UsuarioRepository.obtener_por_external_id(
                session,
                external_id
            )

            if usuario:
                return usuario.id

            raise