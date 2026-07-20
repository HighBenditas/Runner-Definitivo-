from sqlalchemy import insert, select, update
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.tareas_escaneo import TareaEscaneo
from shared.database.models.resultados_tareas import ResultadoTarea
from shared.database.models.sesiones_escaneo import SesionEscaneo
from shared.database.models.objetivos import Objetivo


class TareaRepository:

    @staticmethod
    async def crear(
        session: AsyncSession,
        sesion_id: int,
        herramienta: int,
        nombre_herramienta: str,
        herramienta_id: int,
        version_usada_id: int,
        orden_ejecucion: int,
        input_params: dict
    ):
        query = (
            insert(TareaEscaneo)
            .values(
                sesion_id=sesion_id,
                herramienta=herramienta_id,
                nombre_herramienta=nombre_herramienta,
                herramienta_id=herramienta_id,
                version_usada_id=version_usada_id,
                orden_ejecucion=orden_ejecucion,
                estado="pendiente",
                input_params=input_params,
                fallback_usado=False
            )
            .returning(TareaEscaneo.id)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalar()

    @staticmethod
    async def actualizar_corriendo(session: AsyncSession, tarea_id: int):
        query = (
            update(TareaEscaneo)
            .where(TareaEscaneo.id == tarea_id)
            .values(estado="corriendo", inicio=func.now())
        )
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def actualizar_completado(
        session: AsyncSession,
        tarea_id: int,
        codigo_salida: int,
        duracion: int,
        fallback_usado: bool = False,
        version_fallback_id: int = None
    ):
        query = (
            update(TareaEscaneo)
            .where(TareaEscaneo.id == tarea_id)
            .values(
                estado="completado",
                codigo_salida=codigo_salida,
                duracion_segundos=duracion,
                fallback_usado=fallback_usado,
                version_fallback_id=version_fallback_id,
                fin=func.now()
            )
        )
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def actualizar_fallido(session: AsyncSession, tarea_id: int, mensaje_error: str):
        query = (
            update(TareaEscaneo)
            .where(TareaEscaneo.id == tarea_id)
            .values(
                estado="fallido",
                mensaje_error=mensaje_error,
                codigo_salida=1,
                fin=func.now()
            )
        )
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def obtener_por_id(session: AsyncSession, tarea_id: int):
        query = select(TareaEscaneo).where(TareaEscaneo.id == tarea_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def obtener_usuario_id(session: AsyncSession, tarea_id: int):
        """usuario_id dueño de una tarea (tarea → sesión → objetivo → usuario).

        Sirve para autorizar la lectura de una tarea por su dueño. Devuelve None
        si la tarea no existe o la cadena de FKs no resuelve.
        """
        query = (
            select(Objetivo.usuario_id)
            .select_from(TareaEscaneo)
            .join(SesionEscaneo, TareaEscaneo.sesion_id == SesionEscaneo.id)
            .join(Objetivo, SesionEscaneo.objetivo_id == Objetivo.id)
            .where(TareaEscaneo.id == tarea_id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def listar_recientes(session: AsyncSession, limite: int = 20):
        query = select(TareaEscaneo).order_by(TareaEscaneo.id.desc()).limit(limite)
        result = await session.execute(query)
        return result.scalars().all()


class ResultadoRepository:

    @staticmethod
    async def crear(session: AsyncSession, tarea_id: int, raw_output: str, json_output: dict, nombre_herramienta: str = None):
        query = (
            insert(ResultadoTarea)
            .values(
                tarea_id=tarea_id,
                nombre_herramienta=nombre_herramienta,
                raw_output=raw_output,
                json_output=json_output
            )
            .returning(ResultadoTarea.id)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalar()

    @staticmethod
    async def obtener_por_tarea(session: AsyncSession, tarea_id: int):
        query = select(ResultadoTarea).where(ResultadoTarea.tarea_id == tarea_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
