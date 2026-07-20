from pydantic import BaseModel, field_validator


class UsuarioCreate(BaseModel):
    external_id: str

    @field_validator("external_id")
    @classmethod
    def validar_external_id(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("external_id vacío")
        return value
