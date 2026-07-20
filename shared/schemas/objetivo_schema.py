from pydantic import BaseModel, field_validator


class ObjetivoCreate(BaseModel):
    usuario_id: int
    url_objetivo: str

    @field_validator("url_objetivo")
    @classmethod
    def validar_url(cls, value):

        value = value.strip()

        if not value:
            raise ValueError("URL vacía")

        return value