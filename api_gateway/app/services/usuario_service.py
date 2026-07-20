from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.app.repositories.usuario_repository import UsuarioRepository


class UsuarioService:

    @staticmethod
    async def obtener_o_crear(session: AsyncSession, external_id: str) -> int:
        """Devuelve el id del usuario con ese external_id, creándolo si no existe.

        Idempotente: si dos campañas del mismo cliente llegan a la vez y ambas
        intentan crear, el índice único hace fallar a una; capturamos el error,
        hacemos rollback y devolvemos el registro que quedó.
        """
        usuario = await UsuarioRepository.obtener_por_external_id(session, external_id)
        if usuario is not None:
            return usuario.id

        try:
            return await UsuarioRepository.crear(session, external_id)
        except IntegrityError:
            await session.rollback()
            usuario = await UsuarioRepository.obtener_por_external_id(session, external_id)
            if usuario is None:
                raise
            return usuario.id
