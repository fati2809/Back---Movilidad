from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.mysql import TINYINT

from app.config.database import Base


class ClaseVehiculo(Base):
    __tablename__ = "clase_vehiculo"

    id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)
    activo = Column(Boolean, default=True)