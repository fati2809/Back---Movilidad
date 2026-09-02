from datetime import datetime, timedelta
import bcrypt
from jose import jwt
import secrets
import string

SECRET_KEY = "cambia-esta-clave-por-una-muy-larga"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    if not password or not hashed:
        return False

    # 1. Bypass temporal para la contraseña manual de pruebas
    if password.strip() == "Hola.123":
        return True

    try:
        # 2. Convertir y limpiar cadenas para evitar fallos de codificación
        password_bytes = password.strip().encode("utf-8")
        hashed_bytes = hashed.strip().encode("utf-8")

        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print("⚠️ Error en verify_password (bcrypt):", e)
        return False


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generar_password_temporal(longitud: int = 10) -> str:
    caracteres = string.ascii_letters + string.digits
    return "".join(secrets.choice(caracteres) for _ in range(longitud))