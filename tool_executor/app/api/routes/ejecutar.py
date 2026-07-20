from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from tool_executor.app.core.database import get_db
from tool_executor.app.schemas.ejecutar_schema import EjecutarRequest
from tool_executor.app.services.executor_service import ExecutorService

router = APIRouter(prefix="/ejecutar", tags=["Executor"])


@router.post("/")
async def ejecutar_herramienta(
    data: EjecutarRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    tarea_id = await ExecutorService.ejecutar(session, data, background_tasks)
    return {
        "message": "tarea iniciada",
        "tarea_id": tarea_id,
        "estado": "pendiente"
    }


@router.get("/tareas")
async def listar_tareas(limite: int = 20, session: AsyncSession = Depends(get_db)):
    tareas = await ExecutorService.listar_tareas(session, limite)
    return tareas


@router.get("/tareas/{tarea_id}")
async def obtener_tarea(
    tarea_id: int,
    usuario_id: int | None = None,
    session: AsyncSession = Depends(get_db),
):
    # Si se pasa ?usuario_id=, se valida que la tarea le pertenezca (404 si no).
    tarea, resultado = await ExecutorService.obtener_tarea(session, tarea_id, usuario_id)
    return {
        "tarea_id": tarea.id,
        "estado": tarea.estado,
        "herramienta_id": tarea.herramienta,
        "nombre_herramienta": tarea.nombre_herramienta,
        "input_params": tarea.input_params,
        "fallback_usado": tarea.fallback_usado,
        "codigo_salida": tarea.codigo_salida,
        "duracion_segundos": tarea.duracion_segundos,
        "mensaje_error": tarea.mensaje_error,
        "resultado": {
            "raw_output": resultado.raw_output,
            "json_output": resultado.json_output
        } if resultado else None
    }
