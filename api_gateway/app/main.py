from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.internal_auth import verificar_token_interno

from api_gateway.app.api.routes import objetivos
from api_gateway.app.api.routes import sesiones
from api_gateway.app.api.routes import usuarios
from api_gateway.app.api.routes import proxy

app = FastAPI(
    title="Dani-ETH API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas funcionales protegidas con el token interno (GET / queda público).
_auth = [Depends(verificar_token_interno)]
app.include_router(usuarios.router, dependencies=_auth)
app.include_router(objetivos.router, dependencies=_auth)
app.include_router(sesiones.router, dependencies=_auth)
app.include_router(proxy.router, dependencies=_auth)

@app.get("/")
def root():
    return {"message": "Dani-ETH funcionando"}