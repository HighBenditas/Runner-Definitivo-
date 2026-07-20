from sqlalchemy import insert, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.herramientas import Herramienta


class HerramientaRepository:

    @staticmethod
    async def crear(
        session: AsyncSession,
        nombre: str,
        descripcion: str,
        esquema_input: dict,
        esquema_output: dict,
        version_actual: str,
        nombre_UI: str = None,
        casos_usos: list = None,
        categoria: str = None,
        estado: int = 1
    ):
        query = (
            insert(Herramienta)
            .values(
                nombre=nombre,
                nombre_UI=nombre_UI,
                descripcion=descripcion,
                casos_usos=casos_usos,
                categoria=categoria,
                esquema_input=esquema_input,
                esquema_output=esquema_output,
                version_actual=version_actual,
                estado=estado
            )
            .returning(Herramienta.id)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalar()

    @staticmethod
    async def obtener_por_nombre(session: AsyncSession, nombre: str):
        query = select(Herramienta).where(Herramienta.nombre == nombre)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def obtener_todas(session: AsyncSession):
        query = select(Herramienta).where(Herramienta.estado == 1)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def actualizar(session: AsyncSession, nombre: str, **campos):
        campos["updated_at"] = func.now()
        query = (
            update(Herramienta)
            .where(Herramienta.nombre == nombre)
            .values(**campos)
        )
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def actualizar_version_activa(
        session: AsyncSession,
        herramienta_id: int,
        version_id: int,
        version_str: str
    ):
        query = (
            update(Herramienta)
            .where(Herramienta.id == herramienta_id)
            .values(version_actual=version_str, updated_at=func.now())
        )
        await session.execute(query)
        await session.commit()
