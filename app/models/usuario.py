from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import BigInteger

from sqlalchemy.orm import relationship

from app.config.database import Base
from app.models.rol import Rol


class Usuario(Base):

    __tablename__ = "usuarios"


    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )


    nombre = Column(
        String(100)
    )


    email = Column(
        String(150),
        unique=True
    )


    password_hash = Column(
        String(255)
    )


    activo = Column(
        Boolean,
        default=True
    )


    must_change_password = Column(
        Boolean,
        default=True,
        nullable=False
    )


    rol_id = Column(
        BigInteger,
        ForeignKey("rol.id")
    )


    rol = relationship(
        Rol,
         back_populates="usuarios"
    )