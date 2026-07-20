from fastapi import Depends, FastAPI

from shared.internal_auth import verificar_token_interno
from tool_registry.app.api.routes.herramientas import router as herramientas_router
from tool_registry.app.api.routes.versiones import router as versiones_router

app = FastAPI(title="Tool Registry API")

# Routers funcionales protegidos con el token interno (GET / público para el
# healthcheck de docker-compose).
_auth = [Depends(verificar_token_interno)]
app.include_router(herramientas_router, dependencies=_auth)
app.include_router(versiones_router, dependencies=_auth)


@app.get("/")
async def root():
    return {"message": "Tool Registry API"}
