"""Autenticación interna entre servicios del runner y con el orquestador.

Todas las llamadas "de servidor a servidor" (orquestador → runner, y entre los
propios servicios del runner) llevan un token compartido en la cabecera
`X-Internal-Token`. Sin él, cualquiera con acceso de red al runner podría lanzar
herramientas o leer resultados de otros clientes, saltándose el aislamiento por
tenant que aplica el orquestador.

Configuración por variable de entorno `INTERNAL_API_TOKEN`:
- Si está VACÍA/sin definir → la verificación se desactiva (modo desarrollo),
  para no romper los despliegues actuales. Se registra una advertencia.
- Si está definida → se exige que las peticiones traigan el mismo valor.

`internal_headers()` arma la cabecera para las llamadas salientes entre
servicios (devuelve {} si no hay token, coherente con el modo desarrollo).
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()

logger = logging.getLogger(__name__)

INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")

if not INTERNAL_API_TOKEN:
    logger.warning(
        "INTERNAL_API_TOKEN no está configurado: la autenticación interna del "
        "runner está DESACTIVADA (modo desarrollo). Configúralo en producción."
    )


async def verificar_token_interno(x_internal_token: str | None = Header(default=None)):
    """Dependencia de FastAPI: exige el token interno si está configurado."""
    if not INTERNAL_API_TOKEN:
        return
    if x_internal_token != INTERNAL_API_TOKEN:
        raise HTTPException(status_code=401, detail="Token interno inválido o ausente")


def internal_headers() -> dict:
    """Cabecera para las llamadas salientes entre servicios ({} en desarrollo)."""
    return {"X-Internal-Token": INTERNAL_API_TOKEN} if INTERNAL_API_TOKEN else {}
