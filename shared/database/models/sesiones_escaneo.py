from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, Text
from shared.database.base import Base


class SesionEscaneo(Base):
    tablename = "sesiones_escaneo"

    id = Column(BigInteger, primary_key=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    estado = Column(String, nullable=False)
    inicio = Column(DateTime, nullable=True)
    fin = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    prompt_ia = Column(Text, nullable=True)