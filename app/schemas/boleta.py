from pydantic import BaseModel
from datetime import date, time


class BoletaCreate(BaseModel):

    lugar: str
    fecha: date
    hora: time

    conductor_nombre: str

    conductor_calle: str | None = None
    conductor_numero: str | None = None
    conductor_numero_interior: str | None = None
    conductor_colonia: str | None = None
    conductor_municipio: str | None = None
    conductor_estado: str | None = None
    conductor_cp: str | None = None
    conductor_telefono: str | None = None
    conductor_correo: str | None = None

    propietario_nombre: str | None = None

    propietario_calle: str | None = None
    propietario_numero: str | None =None
    propietario_numero_interior: str | None = None
    propietario_colonia: str | None = None
    propietario_municipio: str | None = None
    propietario_estado: str | None = None
    propietario_cp: str | None = None

    marca_id: int
    modelo_id: int

    placas: str

    estado_clave: str

    tipo_vehiculo_id: int

    numero_motor: str | None = None
    color: str | None = None
    numero_serie: str | None = None

    licencia: str | None = None
    tarjeta_circulacion: str | None = None
    placas_garantia: str | None = None

    anio: int | None = None

    motivo_catalogo_id: int | None = None
    motivos_catalogo_ids: list[int] | None = None

    fundamento: str | None = None

    numero_parte: str | None = None

    tipo_accidente: str | None = None

    empleado_id: int | None = None

    patrulla: str | None = None

    observaciones: str | None = None

    firma_oficial: str | None = None
    firma_conductor: str |None = None