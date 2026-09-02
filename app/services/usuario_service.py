from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate
)
from app.core.security import hash_password
from app.utils.password_generator import generar_password_temporal
from app.services.email_service import (
    enviar_correo_usuario,
    enviar_correo_recuperacion
)


# =====================================================
# OBTENER LISTA DE USUARIOS
# =====================================================
def obtener_usuarios(db: Session):
    return (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .all()
    )


# =====================================================
# OBTENER USUARIO POR ID
# =====================================================
def obtener_usuario(db: Session, id: int):
    return (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.id == id)
        .first()
    )


# =====================================================
# OBTENER USUARIO POR EMAIL
# =====================================================
def obtener_usuario_por_email(db: Session, email: str):
    return (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.email == email)
        .first()
    )


# =====================================================
# CREAR USUARIO Y ENVIAR CORREO
# =====================================================
async def crear_usuario(db: Session, datos: UsuarioCreate):
    # 1. Verificar si ya existe el correo
    usuario_existente = obtener_usuario_por_email(db, datos.email)
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    # 2. Generar contraseña temporal y hash
    password_temporal = generar_password_temporal()

    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password_hash=hash_password(password_temporal),
        rol_id=datos.rol_id,
        activo=True,
        must_change_password=True
    )

    db.add(usuario)
    db.commit()

    # 3. Cargar la relación del Rol para evitar errores de serialización en la respuesta
    usuario = (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.id == usuario.id)
        .first()
    )

    # 4. Intentar enviar correo con credenciales
    try:
        await enviar_correo_usuario(
            usuario.email,
            password_temporal
        )
    except Exception as e:
        print(f"⚠️ Error al enviar el correo a {usuario.email}: {e}")
        # Mantenemos la creación del usuario exitosa pero dejamos registro en logs

    return usuario


# =====================================================
# ACTUALIZAR USUARIO
# =====================================================
def actualizar_usuario(db: Session, id: int, datos: UsuarioUpdate):
    usuario = obtener_usuario(db, id)

    if not usuario:
        return None

    if datos.nombre is not None:
        usuario.nombre = datos.nombre

    if datos.email is not None:
        usuario.email = datos.email

    if datos.rol_id is not None:
        usuario.rol_id = datos.rol_id

    db.commit()
    db.refresh(usuario)

    return usuario


# =====================================================
# CAMBIAR ESTADO (ACTIVAR / DESACTIVAR)
# =====================================================
def cambiar_estado(db: Session, id: int):
    usuario = obtener_usuario(db, id)

    if not usuario:
        return None

    usuario.activo = not usuario.activo

    db.commit()
    db.refresh(usuario)

    return usuario


# =====================================================
# ELIMINAR USUARIO
# =====================================================
def eliminar_usuario(db: Session, id: int):
    usuario = obtener_usuario(db, id)

    if not usuario:
        return False

    try:
        db.delete(usuario)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar el usuario porque tiene boletas u operaciones relacionadas"
        )

    return True


# =====================================================
# RECUPERAR CONTRASEÑA
# =====================================================
async def recuperar_password(db: Session, email: str):
    usuario = obtener_usuario_por_email(db, email)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="No existe un usuario registrado con ese correo"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=403,
            detail="El usuario se encuentra inactivo"
        )

    # Generar nueva contraseña temporal
    password_temporal = generar_password_temporal()

    usuario.password_hash = hash_password(password_temporal)
    usuario.must_change_password = True

    db.commit()
    db.refresh(usuario)

    # Intentar enviar el correo de recuperación
    try:
        await enviar_correo_recuperacion(
            usuario.email,
            password_temporal
        )
    except Exception as e:
        print(f"⚠️ Error enviando correo de recuperación a {email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="No fue posible enviar el correo con la contraseña temporal"
        )

    return {
        "mensaje": "Se ha enviado una contraseña temporal al correo"
    }