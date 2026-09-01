from datetime import datetime, timedelta

import bcrypt
from jose import jwt
import secrets
import string

SECRET_KEY = "cambia-esta-clave-por-una-muy-larga"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
def generar_password_temporal(longitud: int = 10):
    caracteres = string.ascii_letters + string.digits
    return "".join(
        secrets.choice(caracteres)
        for _ in range(longitud)
    )