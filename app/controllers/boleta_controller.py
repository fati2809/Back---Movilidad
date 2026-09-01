from sqlalchemy.orm import Session
from sqlalchemy import func
import asyncio

from fastapi import HTTPException

from app.models.boleta_infraccion import BoletaInfraccion
from app.models.usuario import Usuario
from app.models.marca import Marca
from app.models.modelo import Modelo
from app.models.estado import Estado
from app.models.tipo_vehiculo import TipoVehiculo
from app.models.clase_vehiculo import ClaseVehiculo
from app.models.motivo_infraccion import MotivoInfraccion

from app.schemas.boleta import BoletaCreate
from app.services.folio_service import generar_folio
from app.services.pdf_service import generar_pdf_boleta
from app.services.email_service import enviar_pdf_correo
from app.schemas.boleta_update import BoletaUpdate

def _normalizar_estado_clave(db: Session, valor: str | None) -> str | None:
    if not valor:
        return None

    valor_limpio = str(valor).strip()
    if not valor_limpio:
        return None

    if valor_limpio.isdigit() and len(valor_limpio) == 2:
        return valor_limpio

    alias = {
        "AG": "01", "BC": "02", "BS": "03", "CM": "04", "CS": "05", "CH": "06",
        "CL": "07", "DG": "08", "GT": "09", "GR": "10", "HG": "11", "JC": "12",
        "MC": "13", "MN": "14", "MS": "15", "NT": "16", "NL": "17", "OC": "18",
        "PL": "19", "QT": "20", "QR": "21", "SL": "22", "SI": "23", "SO": "24",
        "TB": "25", "TL": "26", "TN": "27", "TR": "28", "VC": "29", "YN": "30",
        "ZS": "31", "DF": "09"
    }

    clave = alias.get(valor_limpio.upper())
    if clave:
        return clave

    estado = (
        db.query(Estado)
        .filter(func.lower(Estado.nombre) == valor_limpio.lower())
        .first()
    )
    return estado.clave if estado else valor_limpio


def crear_boleta(
    db: Session,
    datos: BoletaCreate
):

    motivo_ids = list(datos.motivos_catalogo_ids or [])
    if datos.motivo_catalogo_id is not None and datos.motivo_catalogo_id not in motivo_ids:
        motivo_ids.insert(0, datos.motivo_catalogo_id)

    payload = datos.model_dump(exclude_none=True)
    payload["motivos_catalogo_ids"] = (
        ",".join(str(id_motivo) for id_motivo in motivo_ids)
        if motivo_ids else None
    )
    payload["motivo_catalogo_id"] = motivo_ids[0] if motivo_ids else None
    payload["estado_clave"] = _normalizar_estado_clave(db, payload.get("estado_clave"))
    payload["conductor_estado"] = _normalizar_estado_clave(db, payload.get("conductor_estado"))
    payload["propietario_estado"] = _normalizar_estado_clave(db, payload.get("propietario_estado"))

    # ==========================
    # GENERAR FOLIO
    # ==========================
    folio = generar_folio(db)


    # ==========================
    # CREAR BOLETA
    # ==========================
    nueva_boleta = BoletaInfraccion(
        folio=folio,
        **payload
    )


    db.add(nueva_boleta)
    db.commit()
    db.refresh(nueva_boleta)


    # ==========================
    # GENERAR PDF
    # ==========================
    archivo_pdf = generar_pdf_boleta(
        db,
        nueva_boleta
    )


    # ==========================
    # ENVIAR CORREO
    # ==========================
    if nueva_boleta.conductor_correo:

        asyncio.run(
            enviar_pdf_correo(
                nueva_boleta.conductor_correo,
                archivo_pdf
            )
        )


    return nueva_boleta





def obtener_boletas(db: Session):

    boletas = (
        db.query(
            BoletaInfraccion,
            Usuario.nombre
        )
        .outerjoin(
            Usuario,
            Usuario.id == BoletaInfraccion.empleado_id
        )
        .all()
    )


    resultado = []


    for boleta, nombre_empleado in boletas:

        resultado.append({

            "id": boleta.id,
            "folio": boleta.folio,
            "fecha": boleta.fecha,

            "conductor_nombre": boleta.conductor_nombre,

            "placas": boleta.placas,

            "patrulla": boleta.patrulla,

            "observaciones": boleta.observaciones,

            "empleado": nombre_empleado,


            "marca_id": boleta.marca_id,
            "modelo_id": boleta.modelo_id,
            "motivo_catalogo_id": boleta.motivo_catalogo_id

        })


    return resultado







def obtener_boleta_por_id(
        
    db: Session,
    id: int
):

    boleta = (
        db.query(BoletaInfraccion)
        .filter(
            BoletaInfraccion.id == id
        )
        .first()
    )


    if not boleta:

        raise HTTPException(
            status_code=404,
            detail="Boleta no encontrada"
        )



    empleado = (
        db.query(Usuario)
        .filter(
            Usuario.id == boleta.empleado_id
        )
        .first()
    )



    marca = (
        db.query(Marca)
        .filter(
            Marca.id == boleta.marca_id
        )
        .first()
    )



    modelo = (
        db.query(Modelo)
        .filter(
            Modelo.id == boleta.modelo_id
        )
        .first()
    )



    estado_vehiculo = (
        db.query(Estado)
        .filter(
            Estado.clave == boleta.estado_clave
        )
        .first()
    )



    estado_conductor = (
        db.query(Estado)
        .filter(
            Estado.clave == boleta.conductor_estado
        )
        .first()
    )



    estado_propietario = (
        db.query(Estado)
        .filter(
            Estado.clave == boleta.propietario_estado
        )
        .first()
    )



    tipo = (
        db.query(TipoVehiculo)
        .filter(
            TipoVehiculo.id == boleta.tipo_vehiculo_id
        )
        .first()
    )



    clase = None


    if tipo:

        clase = (
            db.query(ClaseVehiculo)
            .filter(
                ClaseVehiculo.id == tipo.clase_id
            )
            .first()
        )



    motivo = (
        db.query(MotivoInfraccion)
        .filter(
            MotivoInfraccion.id == boleta.motivo_catalogo_id
        )
        .first()
    )



    return {


        "id": boleta.id,

        "folio": boleta.folio,

        "fecha": boleta.fecha,

        "hora": boleta.hora,

        "lugar": boleta.lugar,



        # =====================
        # CONDUCTOR
        # =====================

        "conductor_nombre": boleta.conductor_nombre,

        "conductor_calle": boleta.conductor_calle,

        "conductor_numero": boleta.conductor_numero,

        "conductor_numero_interior": boleta.conductor_numero_interior,

        "conductor_colonia": boleta.conductor_colonia,

        "conductor_cp": boleta.conductor_cp,

        "conductor_municipio": boleta.conductor_municipio,

        "conductor_estado": estado_conductor.nombre if estado_conductor else "",

        "conductor_telefono": boleta.conductor_telefono,

        "conductor_correo": boleta.conductor_correo,



        # =====================
        # PROPIETARIO
        # =====================

        "propietario_nombre": boleta.propietario_nombre,

        "propietario_calle": boleta.propietario_calle,

        "propietario_numero": boleta.propietario_numero,

        "propietario_numero_interior": boleta.propietario_numero_interior,

        "propietario_colonia": boleta.propietario_colonia,

        "propietario_cp": boleta.propietario_cp,

        "propietario_municipio": boleta.propietario_municipio,

        "propietario_estado": estado_propietario.nombre if estado_propietario else "",



        # =====================
        # VEHICULO
        # =====================

        "marca": marca.nombre if marca else "",

        "modelo": modelo.nombre if modelo else "",

        "placas": boleta.placas,

        "estado": estado_vehiculo.nombre if estado_vehiculo else "",

        "tipo_vehiculo": tipo.nombre if tipo else "",

        "clase_vehiculo": clase.nombre if clase else "",

        "numero_motor": boleta.numero_motor,

        "numero_serie": boleta.numero_serie,

        "color": boleta.color,



        # =====================
        # GARANTIA
        # =====================

        "licencia": boleta.licencia,

        "tarjeta_circulacion": boleta.tarjeta_circulacion,

        "placas_garantia": boleta.placas_garantia,

        "anio": boleta.anio,



        # =====================
        # INFRACCION
        # =====================

        "motivo": motivo.descripcion if motivo else "",

        "fundamento": boleta.fundamento,

        "numero_parte": boleta.numero_parte,

        "tipo_accidente": boleta.tipo_accidente,



        # =====================
        # OFICIAL
        # =====================

        "empleado_id": boleta.empleado_id,

        "empleado": empleado.nombre if empleado else "",

        "patrulla": boleta.patrulla,

        "observaciones": boleta.observaciones,



        # =====================
        # FIRMAS
        # =====================

        "firma_oficial": boleta.firma_oficial,

        "firma_conductor": boleta.firma_conductor

    }

def actualizar_boleta(
    db: Session,
    id: int,
    datos: BoletaUpdate
):

    boleta = db.query(BoletaInfraccion).filter(
        BoletaInfraccion.id == id
    ).first()

    if not boleta:
        raise HTTPException(
            status_code=404,
            detail="Boleta no encontrada"
        )

    datos_actualizados = datos.model_dump(exclude_none=True)

    for campo, valor in datos_actualizados.items():
        setattr(
            boleta,
            campo,
            valor
        )

    db.commit()
    db.refresh(boleta)

    return boleta

def eliminar_boleta(
    db: Session,
    id: int
):

    boleta = db.query(BoletaInfraccion).filter(
        BoletaInfraccion.id == id
    ).first()


    if not boleta:
        raise HTTPException(
            status_code=404,
            detail="Boleta no encontrada"
        )


    db.delete(boleta)
    db.commit()


    return {
        "mensaje": "Boleta eliminada correctamente"
    }