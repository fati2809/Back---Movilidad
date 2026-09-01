from sqlalchemy.orm import Session

from app.models.marca import Marca
from app.models.modelo import Modelo
from app.models.estado import Estado
from app.models.tipo_vehiculo import TipoVehiculo
from app.models.motivo_infraccion import MotivoInfraccion
from app.models.clase_vehiculo import ClaseVehiculo
import requests

def obtener_marcas(db:Session):

    return db.query(Marca).all()



def obtener_modelos(
    db:Session,
    marca_id:int
):

    return db.query(Modelo)\
        .filter(
            Modelo.marca_id == marca_id
        ).all()



def obtener_estados(db:Session):

    return db.query(Estado).all()



def obtener_tipos_vehiculo(
    db: Session,
    clase_id: int
):

    return (
        db.query(TipoVehiculo)
        .filter(
            TipoVehiculo.clase_id == clase_id,
            TipoVehiculo.activo == True
        )
        .all()
    )


def obtener_motivos(db: Session):

    motivos = (
        db.query(MotivoInfraccion)
        .filter(MotivoInfraccion.activo == True)
        .order_by(
            MotivoInfraccion.articulo,
            MotivoInfraccion.fraccion,
            MotivoInfraccion.inciso,
            MotivoInfraccion.numeral
        )
        .all()
    )

    return motivos

def obtener_clases_vehiculo(db: Session):

    return (
        db.query(ClaseVehiculo)
        .filter(ClaseVehiculo.activo == True)
        .all()
    )

def obtener_codigo_postal(cp: str):

    if not cp.isdigit() or len(cp) != 5:
        return {
            "encontrado": False,
            "mensaje": "El código postal debe tener 5 dígitos"
        }

    url = f"https://postali.app/api/v1/mx/cp/{cp}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 404:
            return {
                "encontrado": False,
                "mensaje": "Código postal no encontrado"
            }

        response.raise_for_status()

        data = response.json()

        return {
            "encontrado": True,
            "codigo_postal": data.get("cp"),
            "estado": data.get("estado"),
            "municipio": data.get("municipio")
        }

    except requests.RequestException as error:

        print("Error consultando código postal:", error)

        return {
            "encontrado": False,
            "mensaje": "Error consultando código postal"
        }