from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.schemas.auth_schema import Login

from app.controllers.auth_controller import iniciar_sesion

from app.config.database import SessionLocal


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/login")
def login(data: Login, db: Session = Depends(get_db)):

    return iniciar_sesion(
        db,
        data.email,
        data.password
    )