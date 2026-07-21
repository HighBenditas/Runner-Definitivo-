from typing import Optional
from pydantic import BaseModel


class SesionCreate(BaseModel):
    id_usuario: Optional[int] = None
    objetivo_id: Optional[int] = None