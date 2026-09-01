from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import catalogos_controller

router = APIRouter(
    prefix="/catalogos",
    tags=["Catálogos"]
)

@router.get("/marcas")
def marcas(db: Session = Depends(get_db)):
    return catalogos_controller.obtener_marcas(db)


@router.get("/modelos/{marca_id}")
def modelos(
    marca_id: int,
    db: Session = Depends(get_db)
):
    return catalogos_controller.obtener_modelos(db, marca_id)


@router.get("/estados")
def estados(db: Session = Depends(get_db)):
    return catalogos_controller.obtener_estados(db)


# ========= CLASES =========

@router.get("/clases-vehiculo")
def clases_vehiculo(
    db: Session = Depends(get_db)
):
    return catalogos_controller.obtener_clases_vehiculo(db)


# ========= TIPOS =========

@router.get("/tipos-vehiculo/{clase_id}")
def tipos_vehiculo(
    clase_id: int,
    db: Session = Depends(get_db)
):
    return catalogos_controller.obtener_tipos_vehiculo(
        db,
        clase_id
    )


@router.get("/motivos")
def motivos(db: Session = Depends(get_db)):
    return catalogos_controller.obtener_motivos(db)

@router.get("/codigo-postal/{cp}")
def codigo_postal(cp: str):
    return catalogos_controller.obtener_codigo_postal(cp)