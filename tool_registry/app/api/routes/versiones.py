from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from tool_registry.app.core.database import get_db
from tool_registry.app.schemas.version_schema import VersionCreate
from tool_registry.app.services.version_service import VersionService

router = APIRouter(prefix="/herramientas", tags=["Versiones"])


@router.get("/{nombre}/versiones/fallback")
async def obtener_fallback(nombre: str, session: AsyncSession = Depends(get_db)):
    fallback = await VersionService.obtener_fallback(session, nombre)
    if not fallback:
        return {"message": "no hay version de fallback disponible"}
    return _version_to_dict(fallback)


@router.get("/{nombre}/versiones")
async def listar_versiones(nombre: str, session: AsyncSession = Depends(get_db)):
    versiones = await VersionService.listar_versiones(session, nombre)
    return [_version_to_dict(v) for v in versiones]


def _version_to_dict(v):
    return {
        "id": v.id,
        "id_herramienta": v.id_herramienta,
        "version": v.version,
        "docker_imagen": v.docker_imagen,
        "activo": v.activo,
        "disponible": v.disponible,
        "notas_version": v.notas_version,
        "estado_check": float(v.estado_check) if v.estado_check is not None else None,
        "created_at": v.created_at.isoformat() if v.created_at else None
    }


@router.post("/{nombre}/versiones")
async def agregar_version(
    nombre: str,
    data: VersionCreate,
    session: AsyncSession = Depends(get_db)
):
    version_id = await VersionService.agregar_version(session, nombre, data)
    return {"message": "version agregada", "version_id": version_id}


@router.put("/{nombre}/versiones/{version}/activar")
async def activar_version(
    nombre: str,
    version: str,
    session: AsyncSession = Depends(get_db)
):
    version_id = await VersionService.activar_version(session, nombre, version)
    return {"message": "version activada", "version_id": version_id}


@router.put("/{nombre}/versiones/{version}/marcar-fallida")
async def marcar_version_fallida(
    nombre: str,
    version: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Marca una version como no disponible y activa automaticamente
    la version de fallback. El executor llama a este endpoint
    cuando una version falla al ejecutarse.
    """
    resultado = await VersionService.marcar_fallida_y_activar_fallback(session, nombre, version)
    return resultado
