from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from shared.database.base import Base


class Usuario(Base):
    """Usuario del runner.

    `external_id` guarda el identificador externo del usuario tal como lo maneja
    el orquestador: el `uid` de Firebase (= tenant). Es la clave para resolver
    (get-or-create) el mismo usuario del runner en cada campaña de un cliente.

    La tabla `usuarios` ya existía en la BD (Supabase) referenciada por la FK
    `objetivos.usuario_id`. Tiene columnas NOT NULL sin default (nombre, email,
    password_hash, rol) pensadas para cuentas que inician sesión; los usuarios
    creados desde el orquestador son *tenants* (su identidad vive en Firebase, no
    se loguean en el runner), así que esos campos se derivan del external_id con
    un password_hash placeholder no utilizable. `id` es IDENTITY (autogenerado).
    `external_id` lo añade scripts/migrations/001_multi_tenant.sql.
    """
    __tablename__ = "usuarios"

    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    rol = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    external_id = Column(String, unique=True, index=True)
