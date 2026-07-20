from sqlalchemy.ext.asyncio import AsyncSession
from tool_registry.app.repositories.herramienta_repository import HerramientaRepository
from tool_registry.app.repositories.version_repository import VersionRepository
from tool_registry.app.core.exceptions import NotFoundException, ConflictException


class HerramientaService:

    @staticmethod
    async def crear_herramienta(session: AsyncSession, data):
        existente = await HerramientaRepository.obtener_por_nombre(session, data.nombre)
        if existente:
            raise ConflictException(detail=f"Herramienta '{data.nombre}' ya existe")

        herramienta_id = await HerramientaRepository.crear(
            session=session,
            nombre=data.nombre,
            nombre_UI=data.nombre_UI,
            descripcion=data.descripcion,
            casos_usos=data.casos_usos,
            categoria=data.categoria,
            esquema_input=data.esquema_input,
            esquema_output=data.esquema_output,
            version_actual=data.version_inicial
        )

        version_id = await VersionRepository.crear(
            session=session,
            id_herramienta=herramienta_id,
            version=data.version_inicial,
            docker_imagen=data.docker_imagen,
            notas_version=data.notas_version
        )

        await VersionRepository.activar(session, version_id)
        await HerramientaRepository.actualizar_version_activa(
            session=session,
            herramienta_id=herramienta_id,
            version_id=version_id,
            version_str=data.version_inicial
        )

        return herramienta_id

    @staticmethod
    async def listar_herramientas(session: AsyncSession):
        return await HerramientaRepository.obtener_todas(session)

    @staticmethod
    async def obtener_herramienta(session: AsyncSession, nombre: str):
        herramienta = await HerramientaRepository.obtener_por_nombre(session, nombre)
        if not herramienta:
            raise NotFoundException(detail=f"Herramienta '{nombre}' no encontrada")
        return herramienta

    @staticmethod
    async def actualizar_herramienta(session: AsyncSession, nombre: str, data):
        herramienta = await HerramientaRepository.obtener_por_nombre(session, nombre)
        if not herramienta:
            raise NotFoundException(detail=f"Herramienta '{nombre}' no encontrada")

        campos = data.model_dump(exclude_unset=True)
        if campos:
            await HerramientaRepository.actualizar(session, nombre, **campos)

        return await HerramientaRepository.obtener_por_nombre(session, nombre)

    @staticmethod
    async def listar_para_orquestador(session: AsyncSession):
        herramientas = await HerramientaRepository.obtener_todas(session)
        return [
            {
                "nombre": h.nombre,
                "descripcion": h.descripcion,
                "casos_usos": h.casos_usos,
                "categoria": h.categoria,
                "esquema_input": h.esquema_input,
                "esquema_output": h.esquema_output,
                "version_activa": h.version_actual
            }
            for h in herramientas
        ]
