from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from shared.internal_auth import verificar_token_interno
from shared.auth import verificar_usuario

from api_gateway.app.api.routes import objetivos
from api_gateway.app.api.routes import sesiones
from api_gateway.app.api.routes import usuarios
from api_gateway.app.api.routes import proxy
from api_gateway.app.api.routes import auth


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


protected_dependencies = [
    Depends(verificar_token_interno),
    Depends(verificar_usuario)
]


app.include_router(
    usuarios.router,
    dependencies=protected_dependencies
)

app.include_router(
    objetivos.router,
    dependencies=protected_dependencies
)

app.include_router(
    sesiones.router,
    dependencies=protected_dependencies
)

app.include_router(
    proxy.router,
    dependencies=protected_dependencies
)


# ESTE NO LLEVA JWT
app.include_router(
    auth.router
)


@app.get("/")
def root():
    return {
        "message": "Dani-ETH funcionando"
    }