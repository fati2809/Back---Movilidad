import csv
from io import StringIO

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.boleta_infraccion import BoletaInfraccion
from app.models.usuario import Usuario
from app.models.motivo_infraccion import MotivoInfraccion
from app.models.tipo_vehiculo import TipoVehiculo


# =====================================================
# RESUMEN DEL DASHBOARD
# =====================================================

def obtener_resumen(db: Session):

    # -------------------------------------------------
    # TOTAL DE BOLETAS
    # -------------------------------------------------

    total_boletas = (
        db.query(
            func.count(BoletaInfraccion.id)
        )
        .scalar()
        or 0
    )


    # -------------------------------------------------
    # BOLETAS DEL MES ACTUAL
    # -------------------------------------------------

    boletas_mes = (
        db.query(
            func.count(BoletaInfraccion.id)
        )
        .filter(
            extract(
                "month",
                BoletaInfraccion.fecha
            )
            ==
            extract(
                "month",
                func.current_date()
            )
        )
        .filter(
            extract(
                "year",
                BoletaInfraccion.fecha
            )
            ==
            extract(
                "year",
                func.current_date()
            )
        )
        .scalar()
        or 0
    )


    # -------------------------------------------------
    # AGENTES ACTIVOS
    # -------------------------------------------------

    agentes_activos = (
        db.query(
            func.count(Usuario.id)
        )
        .filter(
            Usuario.activo == True
        )
        .scalar()
        or 0
    )


    # -------------------------------------------------
    # PROMEDIO DIARIO
    # -------------------------------------------------

    promedio_diario = 0

    if total_boletas > 0:

        dias_con_boletas = (
            db.query(
                func.count(
                    func.distinct(
                        BoletaInfraccion.fecha
                    )
                )
            )
            .scalar()
            or 1
        )

        promedio_diario = round(
            total_boletas / dias_con_boletas,
            2
        )


    return {
        "total_boletas": total_boletas,
        "boletas_mes": boletas_mes,
        "agentes_activos": agentes_activos,
        "promedio_diario": promedio_diario
    }


# =====================================================
# INFRACCIONES POR MES
# =====================================================

def obtener_por_mes(db: Session):

    resultados = (
        db.query(
            extract(
                "month",
                BoletaInfraccion.fecha
            ).label("mes"),

            func.count(
                BoletaInfraccion.id
            ).label("cantidad")
        )
        .group_by(
            extract(
                "month",
                BoletaInfraccion.fecha
            )
        )
        .order_by(
            extract(
                "month",
                BoletaInfraccion.fecha
            )
        )
        .all()
    )


    nombres_meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    ]


    return [
        {
            "nombre": nombres_meses[
                int(row.mes) - 1
            ],
            "cantidad": row.cantidad
        }
        for row in resultados
    ]


# =====================================================
# INFRACCIONES POR MOTIVO
# =====================================================

def obtener_por_motivo(db: Session):

    resultados = (
        db.query(
            MotivoInfraccion.descripcion.label(
                "nombre"
            ),

            func.count(
                BoletaInfraccion.id
            ).label(
                "cantidad"
            )
        )

        .join(
            MotivoInfraccion,
            BoletaInfraccion.motivo_catalogo_id
            ==
            MotivoInfraccion.id
        )

        .group_by(
            MotivoInfraccion.id,
            MotivoInfraccion.descripcion
        )

        .order_by(
            func.count(
                BoletaInfraccion.id
            ).desc()
        )

        .all()
    )


    return [
        {
            "nombre": row.nombre,
            "cantidad": row.cantidad
        }
        for row in resultados
    ]


# =====================================================
# INFRACCIONES POR AGENTE
# =====================================================

def obtener_por_agente(db: Session):

    resultados = (
        db.query(
            Usuario.nombre.label(
                "nombre"
            ),

            func.count(
                BoletaInfraccion.id
            ).label(
                "cantidad"
            )
        )

        .join(
            Usuario,
            BoletaInfraccion.empleado_id
            ==
            Usuario.id
        )

        .group_by(
            Usuario.id,
            Usuario.nombre
        )

        .order_by(
            func.count(
                BoletaInfraccion.id
            ).desc()
        )

        .all()
    )


    return [
        {
            "nombre": row.nombre,
            "cantidad": row.cantidad
        }
        for row in resultados
    ]


# =====================================================
# INFRACCIONES POR VEHÍCULO
# =====================================================

def obtener_por_vehiculo(db: Session):

    resultados = (
        db.query(
            TipoVehiculo.nombre.label(
                "nombre"
            ),

            func.count(
                BoletaInfraccion.id
            ).label(
                "cantidad"
            )
        )

        .join(
            TipoVehiculo,
            BoletaInfraccion.tipo_vehiculo_id
            ==
            TipoVehiculo.id
        )

        .group_by(
            TipoVehiculo.id,
            TipoVehiculo.nombre
        )

        .order_by(
            func.count(
                BoletaInfraccion.id
            ).desc()
        )

        .all()
    )


    return [
        {
            "nombre": row.nombre,
            "cantidad": row.cantidad
        }
        for row in resultados
    ]


# =====================================================
# DESCARGAR REPORTES CSV
# =====================================================

def descargar_reporte(db: Session, tipo: str):

    reportes_agrupados = {
        "por-mes": obtener_por_mes,
        "por-motivo": obtener_por_motivo,
        "por-agente": obtener_por_agente,
        "por-vehiculo": obtener_por_vehiculo,
    }

    archivo = StringIO(newline="")
    escritor = csv.writer(archivo)

    if tipo == "general":
        filas = (
            db.query(
                BoletaInfraccion.folio,
                BoletaInfraccion.fecha,
                BoletaInfraccion.hora,
                BoletaInfraccion.lugar,
                BoletaInfraccion.conductor_nombre,
                BoletaInfraccion.placas,
                BoletaInfraccion.color,
                BoletaInfraccion.patrulla,
                MotivoInfraccion.descripcion,
                Usuario.nombre,
                TipoVehiculo.nombre,
            )
            .outerjoin(
                MotivoInfraccion,
                BoletaInfraccion.motivo_catalogo_id == MotivoInfraccion.id,
            )
            .outerjoin(
                Usuario,
                BoletaInfraccion.empleado_id == Usuario.id,
            )
            .outerjoin(
                TipoVehiculo,
                BoletaInfraccion.tipo_vehiculo_id == TipoVehiculo.id,
            )
            .order_by(BoletaInfraccion.fecha.desc())
            .all()
        )

        escritor.writerow([
            "Folio", "Fecha", "Hora", "Lugar", "Conductor",
            "Placas", "Color", "Patrulla", "Motivo", "Agente",
            "Tipo de vehículo",
        ])

        for fila in filas:
            escritor.writerow(fila)
    elif tipo in reportes_agrupados:
        escritor.writerow(["Nombre", "Cantidad"])

        for fila in reportes_agrupados[tipo](db):
            escritor.writerow([fila["nombre"], fila["cantidad"]])
    else:
        raise ValueError("Tipo de reporte no válido")

    contenido = "\ufeff" + archivo.getvalue()
    nombre_archivo = f"reporte_{tipo}.csv"

    return StreamingResponse(
        iter([contenido]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{nombre_archivo}"'
            )
        },
    )