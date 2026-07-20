from pydantic import BaseModel

class SesionCreate(BaseModel):
    objetivo_id: int