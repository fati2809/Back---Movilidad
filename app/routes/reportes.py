from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.config.database import get_db

from app.controllers import reportes_controller


router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)


# =====================================================
# RESUMEN
# =====================================================

@router.get("/resumen")
def obtener_resumen(
    db: Session = Depends(get_db)
):

    return reportes_controller.obtener_resumen(
        db
    )


# =====================================================
# POR MES
# =====================================================

@router.get("/por-mes")
def obtener_por_mes(
    db: Session = Depends(get_db)
):

    return reportes_controller.obtener_por_mes(
        db
    )


# =====================================================
# POR MOTIVO
# =====================================================

@router.get("/por-motivo")
def obtener_por_motivo(
    db: Session = Depends(get_db)
):

    return reportes_controller.obtener_por_motivo(
        db
    )


# =====================================================
# POR AGENTE
# =====================================================

@router.get("/por-agente")
def obtener_por_agente(
    db: Session = Depends(get_db)
):

    return reportes_controller.obtener_por_agente(
        db
    )


# =====================================================
# POR VEHÍCULO
# =====================================================

@router.get("/por-vehiculo")
def obtener_por_vehiculo(
    db: Session = Depends(get_db)
):

    return reportes_controller.obtener_por_vehiculo(
        db
    )


# =====================================================
# DESCARGAR REPORTE CSV
# =====================================================

@router.get("/csv/{tipo}")
def descargar_reporte(
    tipo: str,
    db: Session = Depends(get_db)
):

    try:
        return reportes_controller.descargar_reporte(
            db,
            tipo
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error