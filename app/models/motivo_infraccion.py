from sqlalchemy import Column, Integer, String, Boolean
from app.config.database import Base


class MotivoInfraccion(Base):

    __tablename__ = "motivo_infraccion"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    fuente_ingreso = Column(
        String(20),
        nullable=True
    )

    descripcion = Column(
        String(300),
        nullable=False
    )

    articulo = Column(
        String(20),
        nullable=True
    )

    fraccion = Column(
        String(20),
        nullable=True
    )

    inciso = Column(
        String(20),
        nullable=True
    )

    numeral = Column(
        String(20),
        nullable=True
    )

    fundamento = Column(
        String(500),
        nullable=True
    )

    activo = Column(
        Boolean,
        default=True
    )