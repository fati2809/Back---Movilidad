from pydantic import BaseModel, EmailStr
from typing import Optional


class RolResponse(BaseModel):

    id:int
    nombre:str


    class Config:
        from_attributes = True

class UsuarioCreate(BaseModel):

    nombre:str
    email:str
    rol_id:int



class UsuarioUpdate(BaseModel):

    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rol_id: Optional[int] = None



class UsuarioResponse(BaseModel):

    id: int
    nombre: str
    email: str
    activo: bool
    must_change_password: bool
    rol_id: int
    rol: Optional[RolResponse] = None

    class Config:
        from_attributes = True