from sqlalchemy.orm import Session

from app.models.boleta_infraccion import BoletaInfraccion
from app.schemas.boleta import BoletaCreate
from app.services.folio_service import generar_folio
from app.services.pdf_service import generar_pdf_boleta
from app.services.email_service import enviar_pdf_correo

import asyncio


def crear_boleta(
    db: Session,
    datos: BoletaCreate
):

    # Generar folio
    folio = generar_folio(db)

    # Crear boleta
    nueva_boleta = BoletaInfraccion(
        folio=folio,
        **datos.model_dump()
    )

    db.add(nueva_boleta)
    db.commit()
    db.refresh(nueva_boleta)

    # Generar PDF
    archivo_pdf = generar_pdf_boleta(
    db,
    nueva_boleta
    )

    # Enviar correo al conductor
    if nueva_boleta.conductor_correo:
        asyncio.run(
            enviar_pdf_correo(
                nueva_boleta.conductor_correo,
                archivo_pdf
            )
        )

    return nueva_boleta