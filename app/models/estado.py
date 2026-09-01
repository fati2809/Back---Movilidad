from sqlalchemy import Column, String
from app.config.database import Base


class Estado(Base):

    __tablename__ = "estado"


    clave = Column(
        String(2),
        primary_key=True,
        index=True
    )


    nombre = Column(
        String(80),
        nullable=False
    )