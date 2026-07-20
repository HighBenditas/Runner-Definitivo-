from sqlalchemy import Column, BigInteger, Text, ForeignKey
from shared.database.base import Base

class Objetivo(Base):
    __tablename__ = "objetivos"

    id = Column(BigInteger, primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"))
    url_objetivo = Column(Text, nullable=False)