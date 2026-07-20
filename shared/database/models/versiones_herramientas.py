from sqlalchemy import Column, BigInteger, String, Text, Boolean, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from shared.database.base import Base


class VersionHerramienta(Base):
    __tablename__ = "versiones_herramientas"

    id = Column(BigInteger, primary_key=True)
    id_herramienta = Column(BigInteger, ForeignKey("herramientas.id"), nullable=False)
    version = Column(String, nullable=False)
    docker_imagen = Column(String, nullable=False)
    activo = Column(Boolean)
    disponible = Column(Boolean)
    notas_version = Column(Text)
    check_estado = Column(TIMESTAMP(timezone=True))
    estado_check = Column(Numeric)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
