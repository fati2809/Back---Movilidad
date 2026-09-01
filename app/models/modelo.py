from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.config.database import Base


class Modelo(Base):

    __tablename__ = "modelo"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    marca_id = Column(
        Integer,
        ForeignKey("marca.id"),
        nullable=False
    )


    nombre = Column(
        String(100),
        nullable=False
    )


    activo = Column(
        Boolean,
        default=True
    )