from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db

from app.models.usuario import Usuario

from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse
)

from app.controllers import usuario_controller

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)


# =====================================================
# CAMBIAR CONTRASEÑA (usuario logueado)
# =====================================================

@router.patch("/change-password")
def change_password(
    data: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):

    password = data.get("password")


    if not password:
        raise HTTPException(
            status_code=400,
            detail="Password requerida"
        )


    from app.core.security import hash_password


    usuario.password_hash = hash_password(
        password
    )


    usuario.must_change_password = False


    db.commit()

    db.refresh(usuario)


    return {
        "mensaje":"Contraseña actualizada"
    }



# =====================================================
# LISTAR USUARIOS
# =====================================================

@router.get(
    "/",
    response_model=list[UsuarioResponse]
)
def listar_usuarios(
    db: Session = Depends(get_db)
):

    return usuario_controller.obtener_usuarios(
        db
    )



# =====================================================
# OBTENER USUARIO POR ID
# =====================================================

@router.get(
    "/{id}",
    response_model=UsuarioResponse
)
def obtener_usuario(
    id:int,
    db:Session = Depends(get_db)
):

    usuario = usuario_controller.obtener_usuario(
        db,
        id
    )


    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )


    return usuario



# =====================================================
# CREAR USUARIO
# =====================================================

@router.post(
    "/",
    response_model=UsuarioResponse
)
async def crear_usuario(
    datos:UsuarioCreate,
    db:Session = Depends(get_db)
):

    return await usuario_controller.crear_usuario(
        db,
        datos
    )



# =====================================================
# ACTUALIZAR USUARIO
# =====================================================

@router.put(
    "/{id}",
    response_model=UsuarioResponse
)
def actualizar_usuario(
    id:int,
    datos:UsuarioUpdate,
    db:Session = Depends(get_db)
):

    usuario = usuario_controller.actualizar_usuario(
        db,
        id,
        datos
    )


    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )


    return usuario



# =====================================================
# ACTIVAR / DESACTIVAR USUARIO
# =====================================================

@router.patch(
    "/{id}/estado"
)
def cambiar_estado(
    id:int,
    db:Session = Depends(get_db)
):

    usuario = usuario_controller.cambiar_estado(
        db,
        id
    )


    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )


    return {
        "mensaje":"Estado actualizado",
        "activo":usuario.activo
    }



# =====================================================
# ELIMINAR USUARIO
# =====================================================

@router.delete(
    "/{id}"
)
def eliminar_usuario(
    id:int,
    db:Session = Depends(get_db)
):

    eliminado = usuario_controller.eliminar_usuario(
        db,
        id
    )


    if not eliminado:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )


    return {
        "mensaje":"Usuario eliminado"
    }
# =====================================================
# RECUPERAR CONTRASEÑA
# =====================================================

@router.post("/forgot-password")
async def forgot_password(
    data: dict,
    db: Session = Depends(get_db)
):
    email = data.get("email")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="El correo es obligatorio"
        )

    return await usuario_controller.recuperar_password(
        db,
        email
    )