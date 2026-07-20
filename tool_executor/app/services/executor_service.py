import asyncio
import json
import time
import logging

import httpx

from shared.database.session import SessionLocal
from shared.internal_auth import internal_headers
from tool_executor.app.core.config import TOOL_REGISTRY_URL
from tool_executor.app.core.exceptions import NotFoundException, ToolExecutionException
from tool_executor.app.repositories.tarea_repository import TareaRepository, ResultadoRepository

logger = logging.getLogger(__name__)


class ExecutorService:

    @staticmethod
    async def lanzar_container(docker_imagen: str, params: dict, timeout: int = 900):
        params_json = json.dumps(params)
        inicio = time.time()

        proceso = await asyncio.create_subprocess_exec(
            "docker", "run", "--rm", docker_imagen, params_json,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(proceso.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proceso.kill()
            raise ToolExecutionException(detail="El container superó el tiempo límite de ejecución")

        duracion = int(time.time() - inicio)
        return stdout.decode(), stderr.decode(), proceso.returncode, duracion

    @staticmethod
    async def ejecutar_en_background(
        tarea_id: int,
        docker_imagen: str,
        params: dict,
        nombre_herramienta: str = None,
        fallback_imagen: str = None,
        fallback_version_id: int = None
    ):
        try:
            # Marcar como corriendo
            async with SessionLocal() as session:
                await TareaRepository.actualizar_corriendo(session, tarea_id)

            # Ejecutar container fuera de la sesión DB para no bloquearla
            stdout, stderr, codigo_salida, duracion = await ExecutorService.lanzar_container(
                docker_imagen, params
            )

            fallback_usado = False
            version_fallback_id = None

            # Si falló y hay fallback, intentar con la versión anterior
            if codigo_salida != 0 and fallback_imagen:
                logger.warning(f"Tarea {tarea_id}: version activa falló, usando fallback")
                stdout, stderr, codigo_salida, duracion = await ExecutorService.lanzar_container(
                    fallback_imagen, params
                )
                fallback_usado = True
                version_fallback_id = fallback_version_id

                # Notificar al registry para marcar la versión fallida y activar el fallback
                if nombre_herramienta:
                    try:
                        async with httpx.AsyncClient(headers=internal_headers()) as client:
                            # Obtener la versión activa que falló para marcarla
                            resp = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/{nombre_herramienta}/versiones")
                            versiones = resp.json()
                            version_fallida = next(
                                (v for v in versiones if v.get("docker_imagen") == docker_imagen), None
                            )
                            if version_fallida:
                                await client.put(
                                    f"{TOOL_REGISTRY_URL}/herramientas/{nombre_herramienta}/versiones/{version_fallida['version']}/marcar-fallida"
                                )
                                logger.warning(
                                    f"Version '{version_fallida['version']}' marcada como no disponible. "
                                    f"Fallback activado automáticamente."
                                )
                    except Exception as e_reg:
                        logger.error(f"No se pudo notificar al registry sobre versión fallida: {e_reg}")

            # Parsear output
            try:
                json_output = json.loads(stdout)
            except Exception:
                json_output = {"raw": stdout, "error": stderr}

            # Guardar resultado y actualizar estado con sesión fresca
            async with SessionLocal() as session:
                await ResultadoRepository.crear(
                    session=session,
                    tarea_id=tarea_id,
                    nombre_herramienta=nombre_herramienta,
                    raw_output=stdout,
                    json_output=json_output
                )
                await TareaRepository.actualizar_completado(
                    session=session,
                    tarea_id=tarea_id,
                    codigo_salida=codigo_salida,
                    duracion=duracion,
                    fallback_usado=fallback_usado,
                    version_fallback_id=version_fallback_id
                )

            logger.info(f"Tarea {tarea_id} completada en {duracion}s con codigo {codigo_salida}")

        except Exception as e:
            logger.error(f"Tarea {tarea_id} falló: {e}")
            # Sesión fresca para no usar una sesión en estado inválido
            try:
                async with SessionLocal() as session:
                    await TareaRepository.actualizar_fallido(
                        session=session,
                        tarea_id=tarea_id,
                        mensaje_error=str(e)
                    )
            except Exception as e2:
                logger.error(f"No se pudo marcar tarea {tarea_id} como fallida: {e2}")

    @staticmethod
    async def ejecutar(session, data, background_tasks):
        async with httpx.AsyncClient(headers=internal_headers()) as client:
            # Obtener herramienta del registry
            resp = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/{data.herramienta}")
            if resp.status_code == 404:
                raise NotFoundException(detail=f"Herramienta '{data.herramienta}' no encontrada")
            herramienta = resp.json()

            # Obtener versiones
            resp_v = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/{data.herramienta}/versiones")
            versiones = resp_v.json()

            # Obtener fallback
            resp_f = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/{data.herramienta}/versiones/fallback")
            fallback = resp_f.json() if resp_f.status_code == 200 and "id" in resp_f.json() else None

        version_activa = next((v for v in versiones if v.get("activo")), None)
        if not version_activa:
            raise NotFoundException(detail=f"No hay versión activa para '{data.herramienta}'")

        fallback_imagen = fallback.get("docker_imagen") if fallback else None
        fallback_version_id = fallback.get("id") if fallback else None

        # Crear registro de tarea
        tarea_id = await TareaRepository.crear(
            session=session,
            sesion_id=data.sesion_id,
            herramienta=herramienta["id"],
            nombre_herramienta=data.herramienta,
            herramienta_id=herramienta["id"],
            version_usada_id=version_activa["id"],
            orden_ejecucion=data.orden_ejecucion,
            input_params=data.params
        )

        # Lanzar container en background — no bloquea la respuesta
        background_tasks.add_task(
            ExecutorService.ejecutar_en_background,
            tarea_id,
            version_activa["docker_imagen"],
            data.params,
            data.herramienta,
            fallback_imagen,
            fallback_version_id
        )

        return tarea_id

    @staticmethod
    async def obtener_tarea(session, tarea_id: int, usuario_id: int = None):
        tarea = await TareaRepository.obtener_por_id(session, tarea_id)
        if not tarea:
            raise NotFoundException(detail=f"Tarea {tarea_id} no encontrada")
        # Autorización por dueño: si se pasa usuario_id, la tarea debe pertenecerle.
        # Se responde 404 (no 403) para no delatar la existencia de tareas ajenas.
        if usuario_id is not None:
            dueno = await TareaRepository.obtener_usuario_id(session, tarea_id)
            if dueno != usuario_id:
                raise NotFoundException(detail=f"Tarea {tarea_id} no encontrada")
        resultado = await ResultadoRepository.obtener_por_tarea(session, tarea_id)
        return tarea, resultado

    @staticmethod
    async def listar_tareas(session, limite: int = 20):
        tareas = await TareaRepository.listar_recientes(session, limite)
        return [
            {
                "tarea_id": t.id,
                "estado": t.estado,
                "nombre_herramienta": t.nombre_herramienta,
                "input_params": t.input_params,
                "fallback_usado": t.fallback_usado,
                "codigo_salida": t.codigo_salida,
                "duracion_segundos": t.duracion_segundos,
                "mensaje_error": t.mensaje_error,
            }
            for t in tareas
        ]
