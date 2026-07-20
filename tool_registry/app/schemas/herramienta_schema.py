from pydantic import BaseModel
from typing import Optional, Any


class HerramientaCreate(BaseModel):
    nombre: str
    nombre_UI: Optional[str] = None
    descripcion: str
    casos_usos: Optional[list[str]] = None
    categoria: Optional[str] = None
    esquema_input: dict[str, Any]
    esquema_output: dict[str, Any]
    version_inicial: str
    docker_imagen: str
    notas_version: Optional[str] = None


class HerramientaUpdate(BaseModel):
    nombre_UI: Optional[str] = None
    descripcion: Optional[str] = None
    casos_usos: Optional[list[str]] = None
    categoria: Optional[str] = None
    esquema_input: Optional[dict[str, Any]] = None
    esquema_output: Optional[dict[str, Any]] = None
    estado: Optional[int] = None


class HerramientaResponse(BaseModel):
    id: int
    nombre: str
    nombre_UI: Optional[str]
    descripcion: str
    casos_usos: Optional[list]
    categoria: Optional[str]
    esquema_input: dict
    esquema_output: dict
    version_actual: str
    estado: Optional[float]

    class Config:
        from_attributes = True
