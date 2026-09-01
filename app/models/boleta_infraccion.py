from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    Time,
    Text,
    ForeignKey,
    SmallInteger,
    TIMESTAMP
)

from sqlalchemy.sql import func

from app.config.database import Base


class BoletaInfraccion(Base):

    __tablename__ = "boleta_infraccion"


    id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )


    folio = Column(
        String(30),
        unique=True,
        nullable=False
    )


    lugar = Column(
        String(250),
        nullable=False
    )


    fecha = Column(
        Date,
        nullable=False
    )


    hora = Column(
        Time,
        nullable=False
    )


    # =========================
    # CONDUCTOR
    # =========================

    conductor_nombre = Column(
        String(120),
        nullable=False
    )

    conductor_calle = Column(
        String(150)
    )

    conductor_numero = Column(
        String(15)
    )

    conductor_numero_interior = Column(
        String(15)
    )

    conductor_colonia = Column(
        String(100)
    )

    conductor_municipio = Column(
        String(100)
    )

    conductor_estado = Column(
        String(2),
        ForeignKey("estado.clave")
    )

    conductor_cp = Column(
        String(5)
    )

    conductor_telefono = Column(
        String(10)
    )

    conductor_correo = Column(
        String(120)
    )


    # =========================
    # PROPIETARIO
    # =========================

    propietario_nombre = Column(
        String(120)
    )

    propietario_calle = Column(
        String(150)
    )

    propietario_numero = Column(
        String(15)
    )

    propietario_numero_interior = Column(
        String(15)
    )

    propietario_colonia = Column(
        String(100)
    )

    propietario_municipio = Column(
        String(100)
    )

    propietario_estado = Column(
        String(2),
        ForeignKey("estado.clave")
    )

    propietario_cp = Column(
        String(5)
    )


    # =========================
    # VEHICULO
    # =========================

    marca_id = Column(
        Integer,
        ForeignKey("marca.id"),
        nullable=False
    )


    modelo_id = Column(
        Integer,
        ForeignKey("modelo.id"),
        nullable=False
    )


    placas = Column(
        String(10),
        nullable=False
    )


    estado_clave = Column(
        String(2),
        ForeignKey("estado.clave"),
        nullable=False
    )


    tipo_vehiculo_id = Column(
        Integer,
        ForeignKey("tipo_vehiculo.id"),
        nullable=False
    )


    numero_motor = Column(
        String(30)
    )


    color = Column(
        String(40)
    )


    numero_serie = Column(
        String(30)
    )


    # =========================
    # GARANTIA
    # =========================

    licencia = Column(
        String(30)
    )


    tarjeta_circulacion = Column(
        String(30)
    )


    placas_garantia = Column(
        String(10)
    )


    anio = Column(
        SmallInteger
    )


    # =========================
    # INFRACCION
    # =========================

    motivo_catalogo_id = Column(
        Integer,
        ForeignKey("motivo_infraccion.id"),
        nullable=True
    )

    motivos_catalogo_ids = Column(
        Text,
        nullable=True,
        default=None
    )

    fundamento = Column(
        Text
    )


    numero_parte = Column(
        String(30)
    )


    tipo_accidente = Column(
        String(30)
    )


    # =========================
    # OFICIAL
    # =========================

    empleado_id = Column(
        BigInteger,
        ForeignKey("usuarios.id")
    )


    patrulla = Column(
        String(20)
    )


    observaciones = Column(
        Text
    )


    # =========================
    # FIRMAS
    # =========================

    firma_oficial = Column(
        Text
    )


    firma_conductor = Column(
        Text
    )


    # =========================
    # FECHAS
    # =========================

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )


    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )