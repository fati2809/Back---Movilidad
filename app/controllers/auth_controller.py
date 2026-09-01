from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.auth_service import login
from app.core.security import create_access_token


def iniciar_sesion(db: Session, email: str, password: str):

    usuario = login(db, email, password)

    # =========================
    # CREDENCIALES INCORRECTAS
    # =========================

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # =========================
    # USUARIO INACTIVO
    # =========================

    if not usuario.activo:
        raise HTTPException(
            status_code=403,
            detail="Usuario inactivo. No tienes permitido iniciar sesión."
        )

    # =========================
    # CREAR TOKEN
    # =========================

    access_token = create_access_token(
        data={
            "sub": str(usuario.id)
        }
    )

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "must_change_password": usuario.must_change_password,
        "user": {
            "id": usuario.id,
            "name": usuario.nombre,
            "email": usuario.email,
            "role_id": usuario.rol.id,
            "role": usuario.rol.nombre,
        }
    }