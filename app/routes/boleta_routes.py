from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os

from pathlib import Path

from app.config.database import get_db
from app.schemas.boleta import BoletaCreate
from app.services.pdf_service import generar_pdf_boleta

from app.controllers.boleta_controller import (
    crear_boleta,
    obtener_boletas,
    obtener_boleta_por_id,
    actualizar_boleta,
    eliminar_boleta
)
from app.schemas.boleta_update import BoletaUpdate


from app.models.boleta_infraccion import BoletaInfraccion


router = APIRouter(
    prefix="/boletas",
    tags=["Boletas"]
)


# CREAR
@router.post("")
def guardar_boleta(
    datos: BoletaCreate,
    db: Session = Depends(get_db)
):
    return crear_boleta(
        db,
        datos
    )


# LISTAR
@router.get("")
def listar_boletas(
    db: Session = Depends(get_db)
):
    return obtener_boletas(db)


# DETALLE
@router.get("/{id}")
def obtener_boleta(
    id: int,
    db: Session = Depends(get_db)
):
    return obtener_boleta_por_id(
        db,
        id
    )


# PDF
@router.get("/{id}/pdf")
def descargar_pdf_boleta(
    id: int,
    db: Session = Depends(get_db)
):

    boleta = db.query(BoletaInfraccion).filter(
        BoletaInfraccion.id == id
    ).first()


    if not boleta:
        raise HTTPException(
            status_code=404,
            detail="Boleta no encontrada"
        )

    base_dir = Path(__file__).resolve().parents[2]
    ruta_pdf = base_dir / "pdfs" / f"{boleta.folio}.pdf"

    if not os.path.exists(ruta_pdf):
        generar_pdf_boleta(db, boleta)

    if not os.path.exists(ruta_pdf):
        raise HTTPException(
            status_code=404,
            detail=f"PDF no encontrado: {ruta_pdf}"
        )

    return FileResponse(
        str(ruta_pdf),
        media_type="application/pdf",
        filename=f"{boleta.folio}.pdf"
    )


# EDITAR


@router.put("/{id}")
def editar_boleta(
    id: int,
    datos: BoletaUpdate,
    db: Session = Depends(get_db)
):
    return actualizar_boleta(
        db,
        id,
        datos
    )


# ELIMINAR
@router.delete("/{id}")
def borrar_boleta(
    id: int,
    db: Session = Depends(get_db)
):
    return eliminar_boleta(
        db,
        id
    )