from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.usuario import Usuario
from app.core.security import verify_password


def login(db: Session, email: str, password: str):
    email_limpio = email.strip().lower()
    print("Email recibido (limpio):", repr(email_limpio))

    # --- DEBUG: Ver todos los correos reales en la BD a la que Render está conectado ---
    todos = db.query(Usuario.email).all()
    print("=== DEBUG BD RENDER ===")
    print("Emails existentes en esta BD:", [u[0] for u in todos])
    print("=======================")

    # Búsqueda insensible a mayúsculas/minúsculas y sin espacios
    usuario = (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(func.lower(Usuario.email) == email_limpio)
        .first()
    )

    # Usuario no existe
    if not usuario:
        print("Usuario no encontrado en la consulta .filter()")
        return None

    print("Hash guardado:", usuario.password_hash)

    # Verificar contraseña
    password_correcta = verify_password(
        password,
        usuario.password_hash
    )

    print("Resultado verify:", password_correcta)

    if not password_correcta:
        return None

    return usuario
