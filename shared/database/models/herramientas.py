from sqlalchemy import Column, BigInteger, String, Text, JSON, Numeric, TIMESTAMP
from sqlalchemy.sql import func
from shared.database.base import Base


class Herramienta(Base):
    __tablename__ = "herramientas"

    id = Column(BigInteger, primary_key=True)
    nombre = Column(String, nullable=False, unique=True)
    nombre_UI = Column(String)
    descripcion = Column(Text, nullable=False)
    casos_usos = Column(JSON)
    categoria = Column(String)
    esquema_input = Column(JSON, nullable=False)
    esquema_output = Column(JSON, nullable=False)
    version_actual = Column(String, nullable=False)
    estado = Column(Numeric)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True))
