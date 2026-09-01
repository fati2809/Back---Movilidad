from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT

from app.config.database import Base


class TipoVehiculo(Base):
    __tablename__ = "tipo_vehiculo"

    id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    clase_id = Column(
        TINYINT(unsigned=True),
        ForeignKey("clase_vehiculo.id"),
        nullable=False
    )
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)