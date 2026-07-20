from pydantic import BaseModel
from typing import Optional, Any


class EjecutarRequest(BaseModel):
    herramienta: str
    params: dict[str, Any]
    sesion_id: int
    orden_ejecucion: int = 1


class TareaEstadoResponse(BaseModel):
    tarea_id: int
    estado: str
    herramienta: str
    input_params: Optional[dict] = None
    mensaje_error: Optional[str] = None
    duracion_segundos: Optional[int] = None
    codigo_salida: Optional[int] = None
    fallback_usado: Optional[bool] = None

    class Config:
        from_attributes = True
