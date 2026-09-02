from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.usuario import Usuario
from app.core.security import verify_password


def login(db: Session, email: str, password: str):
    email_limpio = email.strip().lower()

    usuario = (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(func.lower(Usuario.email) == email_limpio)
        .first()
    )

    if not usuario:
        return None

    # Enviar contraseña limpia
    password_correcta = verify_password(
        password.strip() if password else "",
        usuario.password_hash
    )

    if not password_correcta:
        return None

    return usuario