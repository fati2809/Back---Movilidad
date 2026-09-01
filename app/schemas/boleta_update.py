from pydantic import BaseModel
from typing import Optional


class BoletaUpdate(BaseModel):

    lugar: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None

    conductor_nombre: Optional[str] = None
    conductor_telefono: Optional[str] = None
    conductor_correo: Optional[str] = None

    marca_id: Optional[int] = None
    modelo_id: Optional[int] = None
    placas: Optional[str] = None
    estado_clave: Optional[str] = None

    tipo_vehiculo_id: Optional[int] = None

    color: Optional[str] = None
    observaciones: Optional[str] = None