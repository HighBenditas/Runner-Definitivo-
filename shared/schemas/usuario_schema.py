from pydantic import BaseModel, EmailStr, field_validator


class UsuarioRegister(BaseModel):

    nombre: str
    email: EmailStr
    password: str
    rol: str



class UsuarioLogin(BaseModel):

    email: EmailStr
    password: str



class UsuarioCreate(BaseModel):

    external_id: str

    @field_validator("external_id")
    @classmethod
    def validar_external_id(cls, value):

        value = value.strip()

        if not value:
            raise ValueError("external_id vacío")

        return value