from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import jwt
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.usuario import Usuario


SECRET_KEY = "cambia-esta-clave-por-una-muy-larga"
ALGORITHM = "HS256"


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials


    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )


        usuario_id = payload.get("sub")


        if not usuario_id:
            raise Exception()


    except:

        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )


    usuario = db.query(Usuario).filter(
        Usuario.id == int(usuario_id)
    ).first()


    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )


    return usuario