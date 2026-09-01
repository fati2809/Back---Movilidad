from sqlalchemy import Column, Integer, String, Boolean
from app.config.database import Base


class Marca(Base):

    __tablename__ = "marca"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    nombre = Column(
        String(80),
        nullable=False
    )


    activo = Column(
        Boolean,
        default=True
    )