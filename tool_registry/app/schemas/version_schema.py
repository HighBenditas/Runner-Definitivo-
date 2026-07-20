from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VersionCreate(BaseModel):
    version: str
    docker_imagen: str
    notas_version: Optional[str] = None


class VersionResponse(BaseModel):
    id: int
    id_herramienta: int
    version: str
    docker_imagen: str
    activo: Optional[bool]
    disponible: Optional[bool]
    notas_version: Optional[str]
    estado_check: Optional[float]
    created_at: datetime
    deprecated_at: Optional[datetime]

    class Config:
        from_attributes = True
