from sqlalchemy.orm import Session

from app.services import reportes_service


# =====================================================
# RESUMEN
# =====================================================

def obtener_resumen(
    db: Session
):

    return reportes_service.obtener_resumen(
        db
    )


# =====================================================
# POR MES
# =====================================================

def obtener_por_mes(
    db: Session
):

    return reportes_service.obtener_por_mes(
        db
    )


# =====================================================
# POR MOTIVO
# =====================================================

def obtener_por_motivo(
    db: Session
):

    return reportes_service.obtener_por_motivo(
        db
    )


# =====================================================
# POR AGENTE
# =====================================================

def obtener_por_agente(
    db: Session
):

    return reportes_service.obtener_por_agente(
        db
    )


# =====================================================
# POR VEHÍCULO
# =====================================================

def obtener_por_vehiculo(
    db: Session
):

    return reportes_service.obtener_por_vehiculo(
        db
    )


# =====================================================
# DESCARGAR REPORTE CSV
# =====================================================

def descargar_reporte(
    db: Session,
    tipo: str
):

    return reportes_service.descargar_reporte(
        db,
        tipo
    )