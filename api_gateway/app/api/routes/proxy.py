import os

import httpx
from fastapi import APIRouter, HTTPException, Request

from shared.internal_auth import internal_headers

router = APIRouter(prefix="/proxy", tags=["Proxy"])

TOOL_REGISTRY_URL = "http://tool_registry:8003"
TOOL_EXECUTOR_URL = "http://tool_executor:8004"
API_GATEWAY_URL = "http://api_gateway:8000"

# Usuario por defecto para el flujo de auto-creación del proxy (cuando llega una
# ejecución sin sesion_id). Antes estaba hardcodeado en 1; ahora es configurable.
# El orquestador NO usa este flujo: crea su propio usuario/sesión por tenant.
DEFAULT_PROXY_USER_ID = int(os.getenv("DEFAULT_PROXY_USER_ID", "1"))


# ─── HERRAMIENTAS ────────────────────────────────────────────────────────────

@router.get("/herramientas")
async def listar_herramientas():
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.get("/herramientas/{nombre}/versiones/fallback")
async def obtener_fallback(nombre: str):
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/{nombre}/versiones/fallback")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.get("/herramientas/{nombre}/versiones")
async def listar_versiones(nombre: str):
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/{nombre}/versiones")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.get("/herramientas/para-orquestador")
async def listar_herramientas_orquestador():
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/para-orquestador")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.get("/herramientas/{nombre}")
async def obtener_herramienta(nombre: str):
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.get(f"{TOOL_REGISTRY_URL}/herramientas/{nombre}")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.post("/herramientas")
async def crear_herramienta(request: Request):
    body = await request.json()
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.post(f"{TOOL_REGISTRY_URL}/herramientas/", json=body)
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.put("/herramientas/{nombre}")
async def actualizar_herramienta(nombre: str, request: Request):
    body = await request.json()
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.put(f"{TOOL_REGISTRY_URL}/herramientas/{nombre}", json=body)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


# ─── VERSIONES ───────────────────────────────────────────────────────────────

@router.post("/herramientas/{nombre}/versiones")
async def agregar_version(nombre: str, request: Request):
    body = await request.json()
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.post(f"{TOOL_REGISTRY_URL}/herramientas/{nombre}/versiones", json=body)
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.put("/herramientas/{nombre}/versiones/{version}/activar")
async def activar_version(nombre: str, version: str):
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.put(f"{TOOL_REGISTRY_URL}/herramientas/{nombre}/versiones/{version}/activar")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.put("/herramientas/{nombre}/versiones/{version}/marcar-fallida")
async def marcar_version_fallida(nombre: str, version: str):
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.put(f"{TOOL_REGISTRY_URL}/herramientas/{nombre}/versiones/{version}/marcar-fallida")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


# ─── TAREAS / EXECUTOR ───────────────────────────────────────────────────────

@router.get("/tareas/{tarea_id}")
async def obtener_tarea(tarea_id: int):
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.get(f"{TOOL_EXECUTOR_URL}/ejecutar/tareas/{tarea_id}")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.get("/tareas")
async def listar_tareas(limite: int = 20):
    async with httpx.AsyncClient(headers=internal_headers()) as client:
        r = await client.get(f"{TOOL_EXECUTOR_URL}/ejecutar/tareas", params={"limite": limite})
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.post("/ejecutar")
async def ejecutar_herramienta(request: Request):
    body = await request.json()
    sesion_id = body.get("sesion_id")

    try:
        async with httpx.AsyncClient(timeout=60, headers=internal_headers()) as client:
            if not sesion_id:
                r_obj = await client.post(
                    f"{API_GATEWAY_URL}/objetivos/",
                    json={"usuario_id": DEFAULT_PROXY_USER_ID, "url_objetivo": "http://target.local"}
                )
                if r_obj.status_code not in (200, 201):
                    raise HTTPException(status_code=502, detail=f"Error creando objetivo: {r_obj.text}")
                objetivo_id = r_obj.json().get("objetivo_id")
                if not objetivo_id:
                    raise HTTPException(status_code=502, detail="No se pudo obtener objetivo_id")

                r_ses = await client.post(
                    f"{API_GATEWAY_URL}/sesiones/",
                    json={"objetivo_id": objetivo_id}
                )
                if r_ses.status_code not in (200, 201):
                    raise HTTPException(status_code=502, detail=f"Error creando sesión: {r_ses.text}")
                sesion_id = r_ses.json().get("sesion_id")
                if not sesion_id:
                    raise HTTPException(status_code=502, detail="No se pudo obtener sesion_id")

            payload = {
                "herramienta": body.get("herramienta"),
                "params": body.get("params", {}),
                "sesion_id": sesion_id,
                "orden_ejecucion": body.get("orden_ejecucion", 1),
            }

            r = await client.post(f"{TOOL_EXECUTOR_URL}/ejecutar/", json=payload)
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return r.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))