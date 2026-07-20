from sqlalchemy import Column, BigInteger, String, ForeignKey
from shared.database.base import Base

class SesionEscaneo(Base):
    __tablename__ = "sesiones_escaneo"

    id = Column(BigInteger, primary_key=True)
    objetivo_id = Column(BigInteger, ForeignKey("objetivos.id"))
    estado = Column(String, nullable=False)