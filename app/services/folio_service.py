from sqlalchemy import text
from datetime import datetime


def generar_folio(db):

    ultimo = db.execute(
        text("""
            SELECT folio
            FROM boleta_infraccion
            ORDER BY id DESC
            LIMIT 1
        """)
    ).fetchone()


    anio = datetime.now().year


    if ultimo:
        ultimo_folio = ultimo[0]

        numero = int(ultimo_folio.split("-")[-1])
        nuevo_numero = numero + 1

    else:
        nuevo_numero = 1


    return f"SMMEM-{nuevo_numero:06d}"