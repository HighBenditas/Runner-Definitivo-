from sqlalchemy import Column, BigInteger, SmallInteger, String, Text, JSON, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from shared.database.base import Base


class TareaEscaneo(Base):
    __tablename__ = "tareas_escaneo"

    id = Column(BigInteger, primary_key=True)
    sesion_id = Column(BigInteger, ForeignKey("sesiones_escaneo.id"))
    herramienta = Column(BigInteger, nullable=False)
    nombre_herramienta = Column(String)
    herramienta_id = Column(BigInteger, ForeignKey("herramientas.id"))
    version_usada_id = Column(BigInteger, ForeignKey("versiones_herramientas.id"))
    fallback_usado = Column(Boolean, default=False)
    version_fallback_id = Column(BigInteger, ForeignKey("versiones_herramientas.id"))
    orden_ejecucion = Column(SmallInteger, nullable=False)
    estado = Column(String, nullable=False)
    comando_raw = Column(Text)
    input_params = Column(JSON)
    mensaje_error = Column(Text)
    inicio = Column(TIMESTAMP(timezone=True))
    fin = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    codigo_salida = Column(SmallInteger)
    duracion_segundos = Column(BigInteger)
