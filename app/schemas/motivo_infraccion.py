from pydantic import BaseModel
from typing import Optional


class MotivoInfraccionResponse(BaseModel):
    id: int
    fuente_ingreso: Optional[str] = None
    descripcion: str
    articulo: Optional[str] = None
    fraccion: Optional[str] = None
    inciso: Optional[str] = None
    numeral: Optional[str] = None
    fundamento: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True

class MotivoInfraccionCreate(BaseModel):
    fuente_ingreso: Optional[str] = None
    descripcion: str
    articulo: Optional[str] = None
    fraccion: Optional[str] = None
    inciso: Optional[str] = None
    numeral: Optional[str] = None
    fundamento: Optional[str] = None
    activo: bool = True