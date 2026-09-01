from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.rol import Rol


router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get("/")
def obtener_roles(
    db: Session = Depends(get_db)
):

    return db.query(Rol).all()