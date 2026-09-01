from pydantic import BaseModel


class MarcaResponse(BaseModel):

    id:int
    nombre:str


    class Config:
        from_attributes = True



class ModeloResponse(BaseModel):

    id:int
    marca_id:int
    nombre:str


    class Config:
        from_attributes = True



class EstadoResponse(BaseModel):

    clave:str
    nombre:str


    class Config:
        from_attributes = True



class TipoVehiculoResponse(BaseModel):

    id: int
    clase_id: int
    nombre: str


    class Config:
        from_attributes = True

class MotivoInfraccionResponse(BaseModel):

    id:int
    nombre:str
    fundamento:str | None
    activo:bool


    class Config:
        from_attributes = True

class ClaseVehiculoResponse(BaseModel):

    id: int
    nombre: str

    class Config:
        from_attributes = True