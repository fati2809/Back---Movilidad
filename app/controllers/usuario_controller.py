from sqlalchemy.orm import Session

from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate
)

from app.services import usuario_service



def obtener_usuarios(
    db: Session
):

    return usuario_service.obtener_usuarios(
        db
    )



def obtener_usuario(
    db: Session,
    id: int
):

    return usuario_service.obtener_usuario(
        db,
        id
    )



async def crear_usuario(
    db: Session,
    datos: UsuarioCreate
):

    return await usuario_service.crear_usuario(
        db,
        datos
    )

async def recuperar_password(
    db: Session,
    email: str
):
    return await usuario_service.recuperar_password(
        db,
        email
    )

def actualizar_usuario(
    db: Session,
    id: int,
    datos: UsuarioUpdate
):

    return usuario_service.actualizar_usuario(
        db,
        id,
        datos
    )



def cambiar_estado(
    db: Session,
    id: int
):

    return usuario_service.cambiar_estado(
        db,
        id
    )



def eliminar_usuario(
    db: Session,
    id: int
):

    return usuario_service.eliminar_usuario(
        db,
        id
    )

