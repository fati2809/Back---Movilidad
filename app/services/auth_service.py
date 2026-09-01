from sqlalchemy.orm import Session, joinedload

from app.models.usuario import Usuario
from app.core.security import verify_password


def login(db: Session, email: str, password: str):

    print("Email recibido:", email)

    usuario = (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.email == email)
        .first()
    )

    # Usuario no existe
    if not usuario:
        print("Usuario no encontrado")
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