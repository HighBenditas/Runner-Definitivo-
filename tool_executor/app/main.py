from fastapi import Depends, FastAPI

from shared.internal_auth import verificar_token_interno
from tool_executor.app.api.routes.ejecutar import router as ejecutar_router

app = FastAPI(title="Tool Executor API")

# El router funcional queda protegido con el token interno (GET / público).
app.include_router(ejecutar_router, dependencies=[Depends(verificar_token_interno)])


@app.get("/")
async def root():
    return {"message": "Tool Executor API"}
