from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.versiones_herramientas import VersionHerramienta


class VersionRepository:

    @staticmethod
    async def crear(
        session: AsyncSession,
        id_herramienta: int,
        version: str,
        docker_imagen: str,
        notas_version: str = None
    ):
        query = (
            insert(VersionHerramienta)
            .values(
                id_herramienta=id_herramienta,
                version=version,
                docker_imagen=docker_imagen,
                activo=False,
                disponible=True,
                notas_version=notas_version
            )
            .returning(VersionHerramienta.id)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalar()

    @staticmethod
    async def obtener_por_herramienta_y_version(
        session: AsyncSession,
        id_herramienta: int,
        version: str
    ):
        query = select(VersionHerramienta).where(
            VersionHerramienta.id_herramienta == id_herramienta,
            VersionHerramienta.version == version
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def obtener_versiones_de_herramienta(session: AsyncSession, id_herramienta: int):
        query = (
            select(VersionHerramienta)
            .where(VersionHerramienta.id_herramienta == id_herramienta)
            .order_by(VersionHerramienta.created_at.desc())
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def desactivar_todas(session: AsyncSession, id_herramienta: int):
        query = (
            update(VersionHerramienta)
            .where(VersionHerramienta.id_herramienta == id_herramienta)
            .values(activo=False)
        )
        await session.execute(query)

    @staticmethod
    async def activar(session: AsyncSession, version_id: int):
        query = (
            update(VersionHerramienta)
            .where(VersionHerramienta.id == version_id)
            .values(activo=True)
            .returning(VersionHerramienta.id, VersionHerramienta.version)
        )
        result = await session.execute(query)
        await session.commit()
        return result.one_or_none()

    @staticmethod
    async def marcar_no_disponible(session: AsyncSession, version_id: int):
        query = (
            update(VersionHerramienta)
            .where(VersionHerramienta.id == version_id)
            .values(activo=False, disponible=False)
        )
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def obtener_por_id(session: AsyncSession, version_id: int):
        query = select(VersionHerramienta).where(VersionHerramienta.id == version_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def obtener_fallback(session: AsyncSession, id_herramienta: int):
        query = (
            select(VersionHerramienta)
            .where(
                VersionHerramienta.id_herramienta == id_herramienta,
                VersionHerramienta.disponible == True,
                VersionHerramienta.activo == False
            )
            .order_by(VersionHerramienta.created_at.desc())
            .limit(1)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
