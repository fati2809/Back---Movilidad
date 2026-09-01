from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class Rol(Base):
    __tablename__ = "rol"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    nombre = Column(
        String(50),
        unique=True
    )


    usuarios = relationship(
        "Usuario",
        back_populates="rol"
    )