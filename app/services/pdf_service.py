import tempfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from sqlalchemy.orm import Session
import qrcode
from app.models.usuario import Usuario
from app.models.marca import Marca
from app.models.modelo import Modelo
from app.models.estado import Estado
from app.models.tipo_vehiculo import TipoVehiculo
from app.models.motivo_infraccion import MotivoInfraccion

import base64
import io


# ==========================
# CONFIGURACIÓN GENERAL
# ==========================

ANCHO, ALTO = landscape(letter)
MARGEN_X = 1 * cm
MARGEN_Y = 1 * cm

COLOR_AZUL = colors.HexColor("#1E4E79")
COLOR_GRIS = colors.HexColor("#D9D9D9")
COLOR_NEGRO = colors.black
COLOR_ROJO = colors.HexColor("#C00000")

LOGO_MOVILIDAD = "app/assets/logo_movilidad.jpeg"
LOGO_MARQUES = "app/assets/logo.png"

FUENTE = "Helvetica"
FUENTE_BOLD = "Helvetica-Bold"
TAM_TEXTO = 7.8
TAM_LABEL = 7.8
ALTO_HEADER_SECCION = 0.42 * cm
ALTO_RENGLON = 0.45 * cm
PRIMER_RENGLON_OFFSET = 0.42 * cm
PAD_INFERIOR = 0.15 * cm
GAP_SECCIONES = 0.8 * cm

# Ancho de columnas
GAP_COLUMNAS = 0.4 * cm
ANCHO_UTIL = ANCHO - (2 * MARGEN_X)
ANCHO_COL_IZQ = (ANCHO_UTIL - GAP_COLUMNAS) * 0.58
ANCHO_COL_DER = (ANCHO_UTIL - GAP_COLUMNAS) * 0.42
X_COL_IZQ = MARGEN_X
X_COL_DER = MARGEN_X + ANCHO_COL_IZQ + GAP_COLUMNAS


# ==========================
# HELPERS DE DIBUJO
# ==========================

def wrap_text(pdf, text, font, size, max_width):
    """Parte un texto en líneas que caben en max_width."""
    if not text:
        return []
    palabras = text.split()
    lineas = []
    actual = ""
    for palabra in palabras:
        prueba = (actual + " " + palabra).strip()
        if pdf.stringWidth(prueba, font, size) <= max_width:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def iniciar_seccion(pdf, x, y, ancho, titulo):
    """Dibuja la barra azul de título de una sección y regresa el
    Y donde debe comenzar el contenido interno (debajo de la barra)."""
    pdf.setFillColor(COLOR_AZUL)
    pdf.rect(x, y - ALTO_HEADER_SECCION, ancho, ALTO_HEADER_SECCION, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont(FUENTE_BOLD, 8.5)
    pdf.drawString(x + 0.18 * cm, y - ALTO_HEADER_SECCION + 0.12 * cm, titulo)
    return y - ALTO_HEADER_SECCION


def cerrar_seccion(pdf, x, y_top, ancho, y_bottom):
    """Dibuja el marco del cuerpo de la sección entre y_top y y_bottom."""
    pdf.setStrokeColor(COLOR_GRIS)
    pdf.setLineWidth(0.7)
    pdf.rect(x, y_bottom, ancho, y_top - y_bottom, fill=0)


def campo(pdf, x, y, label, valor, ancho_label=None):
    """Dibuja 'Label: valor' en una posición dada y regresa el ancho usado."""
    pdf.setFont(FUENTE_BOLD, TAM_LABEL)
    pdf.setFillColor(COLOR_NEGRO)
    pdf.drawString(x, y, label)
    ancho_lbl = ancho_label if ancho_label else pdf.stringWidth(label, FUENTE_BOLD, TAM_LABEL) + 0.15 * cm
    pdf.setFont(FUENTE, TAM_TEXTO)
    pdf.drawString(x + ancho_lbl, y, str(valor) if valor else "")
    return ancho_lbl


def checkbox(pdf, x, y, label, marcado=False, lado=0.32 * cm):
    """Dibuja una casilla de verificación con su etiqueta a la izquierda."""
    pdf.setFont(FUENTE, TAM_TEXTO)
    pdf.setFillColor(COLOR_NEGRO)
    pdf.drawString(x, y, label)
    ancho_lbl = pdf.stringWidth(label, FUENTE, TAM_TEXTO)
    caja_x = x + ancho_lbl + 0.2 * cm
    pdf.setStrokeColor(COLOR_NEGRO)
    pdf.rect(caja_x, y - 0.05 * cm, lado, lado, fill=0)
    if marcado:
        pdf.setFont(FUENTE_BOLD, TAM_TEXTO)
        pdf.drawString(caja_x + 0.05 * cm, y - 0.02 * cm, "X")
    return caja_x + lado


# ==========================
# FUNCIÓN PRINCIPAL
# ==========================

def obtener_motivos_boleta(db: Session, boleta):
    ids = []

    if getattr(boleta, "motivos_catalogo_ids", None):
        ids = [
            int(parte.strip())
            for parte in str(boleta.motivos_catalogo_ids).split(",")
            if parte.strip()
        ]

    if getattr(boleta, "motivo_catalogo_id", None) is not None and boleta.motivo_catalogo_id not in ids:
        ids.append(int(boleta.motivo_catalogo_id))

    if not ids:
        return []

    motivos = db.query(MotivoInfraccion).filter(MotivoInfraccion.id.in_(ids)).all()
    mapa = {motivo.id: motivo for motivo in motivos}
    return [mapa[id_motivo] for id_motivo in ids if id_motivo in mapa]


def generar_pdf_boleta(db: Session, boleta):
    base_dir = Path(__file__).resolve().parents[2]
    carpeta = base_dir / "pdfs"
    carpeta.mkdir(exist_ok=True, parents=True)
    ruta = carpeta / f"{boleta.folio}.pdf"
    pdf = canvas.Canvas(str(ruta), pagesize=landscape(letter))

    marca = db.query(Marca).filter(Marca.id == boleta.marca_id).first()
    modelo = db.query(Modelo).filter(Modelo.id == boleta.modelo_id).first()
    estado_vehiculo = db.query(Estado).filter(Estado.clave == boleta.estado_clave).first()
    tipo = db.query(TipoVehiculo).filter(TipoVehiculo.id == boleta.tipo_vehiculo_id).first()
    estado_propietario = db.query(Estado).filter(Estado.clave == boleta.propietario_estado).first()
    estado_conductor = db.query(Estado).filter(
        Estado.clave == getattr(boleta, "conductor_estado", None)
    ).first()
    
    oficial = db.query(Usuario).filter(
    Usuario.id == boleta.empleado_id
    ).first()

    oficial_nombre = oficial.nombre if oficial else ""

    motivos = obtener_motivos_boleta(db, boleta)

    catalogos = {
        "marca": marca.nombre if marca else "",
        "modelo": modelo.nombre if modelo else "",
        "estado_vehiculo": estado_vehiculo.nombre if estado_vehiculo else "",
        "tipo": tipo.nombre if tipo else "",
        "motivos": motivos,
        "motivo_obj": motivos[0] if motivos else None,
        "estado_propietario": estado_propietario.nombre if estado_propietario else "",
        "estado_conductor": estado_conductor.nombre if estado_conductor else "",
    }

    y_header_bottom = dibujar_encabezado(pdf, boleta)

    # ----- Columna izquierda -----
    y = y_header_bottom
    y = dibujar_lugar_fecha(pdf, boleta, y)
    y -= 0.3 * cm
    y = dibujar_conductor(pdf, boleta, catalogos, y)
    y -= 0.3 * cm
    y = dibujar_propietario(pdf, boleta, catalogos, y)
    y -= 0.3 * cm
    y = dibujar_vehiculo(pdf, boleta, catalogos, y)
    y -= 0.3 * cm
    dibujar_observaciones_y_firma_conductor(pdf, boleta, y)

    # ----- Columna derecha -----
    y2 = y_header_bottom
    dibujar_motivo_y_formulo(pdf, boleta, catalogos, y2,oficial_nombre)

    dibujar_pie_pagina(pdf)

    pdf.save()
    return str(ruta)


# ==========================
# ENCABEZADO
# ==========================

def dibujar_encabezado(pdf, boleta):
    y_top = ALTO - MARGEN_Y

    # Logo Secretaría de Movilidad
    try:
        pdf.drawImage(
            ImageReader(LOGO_MOVILIDAD),
            MARGEN_X, y_top - 1 * cm, width=2.5 * cm, height=2.5 * cm,
            preserveAspectRatio=True, mask='auto',
        )
    except Exception:
        pass

    # Logo El Marqués
    try:
        pdf.drawImage(
            ImageReader(LOGO_MARQUES),
            MARGEN_X + 2 * cm, y_top - 2 * cm, width=2 * cm, height=2 * cm,
            preserveAspectRatio=True, mask='auto',
        )
    except Exception:
        pass

    # Texto institucional (junto a los logos)
    tx = MARGEN_X + 5.4 * cm
    pdf.setFillColor(COLOR_AZUL)
    pdf.setFont(FUENTE_BOLD, 15)
    pdf.drawString(tx, y_top - 0.8 * cm, "SECRETARÍA DE MOVILIDAD")
    pdf.setFillColor(COLOR_NEGRO)
    pdf.setFont(FUENTE, 11)
    pdf.drawString(tx, y_top - 1.4 * cm, "Municipio de El Marqués")
    pdf.setFont(FUENTE, 9)
    pdf.setFillColor(colors.grey)
    pdf.drawString(tx, y_top - 1.9 * cm, "Gobierno Municipal")

    # Título
    pdf.setFillColor(COLOR_NEGRO)
    pdf.setFont(FUENTE_BOLD, 14)

    pdf.drawRightString(
        ANCHO - 3.5*cm,
        y_top - 0.8*cm,
        "BOLETA DE INFRACCIÓN"
    )


    # Folio
    pdf.setFillColor(COLOR_ROJO)
    pdf.setFont(FUENTE_BOLD, 11)

    pdf.drawRightString(
        ANCHO - 3.5*cm,
        y_top - 1.35*cm,
        f"Folio: {boleta.folio}"
    )


    # QR al lado
    crear_qr(
        pdf,
        boleta,
        ANCHO - 2.8*cm,
        y_top - 2.2*cm,
        1.7*cm
    )
    # Línea separadora
    pdf.setStrokeColor(COLOR_AZUL)
    pdf.setLineWidth(2)
    y_linea = y_top - 2.3 * cm
    pdf.line(MARGEN_X, y_linea, ANCHO - MARGEN_X, y_linea)

    return y_linea - 0.3 * cm


# ==========================
# LUGAR Y FECHA (col. izquierda)
# ==========================

def dibujar_lugar_fecha(pdf, boleta, y_top):
    alto_cuerpo = .8 * cm
    y_contenido = iniciar_seccion(pdf, X_COL_IZQ, y_top, ANCHO_COL_IZQ, "LUGAR Y FECHA")
    yy = y_contenido - 0.5 * cm

    campo(pdf, X_COL_IZQ + 0.25 * cm, yy, "Lugar:", boleta.lugar)
    campo(pdf, X_COL_IZQ + 7 * cm, yy, "Fecha:", boleta.fecha.strftime("%d/%m/%Y"))
    campo(pdf, X_COL_IZQ + 11 * cm, yy, "Hora:", boleta.hora.strftime("%H:%M"))
    yy -= ALTO_RENGLON

    y_bottom = y_contenido - alto_cuerpo
    cerrar_seccion(pdf, X_COL_IZQ, y_contenido, ANCHO_COL_IZQ, y_bottom)
    return y_bottom


# ==========================
# CONDUCTOR (col. izquierda)
# ==========================

def dibujar_conductor(pdf, boleta, catalogos, y_top):
    alto_cuerpo = 2 * cm
    y_contenido = iniciar_seccion(pdf, X_COL_IZQ, y_top, ANCHO_COL_IZQ, "CONDUCTOR")
    yy = y_contenido - 0.5 * cm
    x0 = X_COL_IZQ + 0.25 * cm

    direccion = (
    f"{boleta.conductor_calle} "
    f"No. {boleta.conductor_numero}"
    f"{('-'+boleta.conductor_numero_interior) if boleta.conductor_numero_interior else ''}, "
    f"{boleta.conductor_colonia}, "
    f"C.P. {boleta.conductor_cp}"
)
    # Dirección con salto de línea
    pdf.setFont(FUENTE_BOLD, TAM_LABEL)
    pdf.setFillColor(COLOR_NEGRO)
    pdf.drawString(x0, yy, "Dirección:")

    lineas = wrap_text(
        pdf,
        direccion,
        FUENTE,
        TAM_TEXTO,
        ANCHO_COL_IZQ - 2 * cm
    )

    x_texto = x0 + 1.5 * cm

    for linea in lineas:
        pdf.setFont(FUENTE, TAM_TEXTO)
        pdf.drawString(x_texto, yy, linea)
        yy -= 0.35 * cm


    yy -= 0.1 * cm
        
    campo(
    pdf,
    x0,
    yy,
    "Ubicación:",
    f"{boleta.conductor_municipio}, {catalogos['estado_conductor']}"
)

    yy -= ALTO_RENGLON
    campo(pdf, x0, yy, "Teléfono:", boleta.conductor_telefono)
    campo(pdf, X_COL_IZQ + 9 * cm, yy, "Correo:", boleta.conductor_correo)

    y_bottom = y_contenido - alto_cuerpo
    cerrar_seccion(pdf, X_COL_IZQ, y_contenido, ANCHO_COL_IZQ, y_bottom)
    return y_bottom


# ==========================
# PROPIETARIO (col. izquierda)
# ==========================

def dibujar_propietario(pdf, boleta, catalogos, y_top):
    alto_cuerpo = 2 * cm

    y_contenido = iniciar_seccion(
        pdf,
        X_COL_IZQ,
        y_top,
        ANCHO_COL_IZQ,
        "PROPIETARIO"
    )

    yy = y_contenido - 0.5 * cm
    x0 = X_COL_IZQ + 0.25 * cm

    campo(
        pdf,
        x0,
        yy,
        "Nombre:",
        boleta.propietario_nombre
    )

    yy -= ALTO_RENGLON


    direccion = (
        f"{boleta.propietario_calle} "
        f"No. {boleta.propietario_numero}"
        f"{('-' + boleta.propietario_numero_interior) if boleta.propietario_numero_interior else ''}, "
        f"{boleta.propietario_colonia}, "
        f"C.P. {boleta.propietario_cp}"
    )


    # Dirección con salto de línea
    pdf.setFont(FUENTE_BOLD, TAM_LABEL)
    pdf.drawString(x0, yy, "Dirección:")

    lineas = wrap_text(
        pdf,
        direccion,
        FUENTE,
        TAM_TEXTO,
        ANCHO_COL_IZQ - 2 * cm
    )

    x_texto = x0 + 1.5 * cm

    for linea in lineas:
        pdf.setFont(FUENTE, TAM_TEXTO)
        pdf.drawString(x_texto, yy, linea)
        yy -= 0.35 * cm


    yy -= 0.1 * cm


    campo(
        pdf,
        x0,
        yy,
        "Ubicación:",
        f"{boleta.propietario_municipio}, {catalogos['estado_propietario']}"
    )


    y_bottom = y_contenido - alto_cuerpo

    cerrar_seccion(
        pdf,
        X_COL_IZQ,
        y_contenido,
        ANCHO_COL_IZQ,
        y_bottom
    )

    return y_bottom

# ==========================
# VEHÍCULO + GARANTÍA (col. izquierda)
# ==========================

def dibujar_vehiculo(pdf, boleta, catalogos, y_top):
    alto_cuerpo = 3.8 * cm
    y_contenido = iniciar_seccion(pdf, X_COL_IZQ, y_top, ANCHO_COL_IZQ, "VEHÍCULO")
    yy = y_contenido - 0.5 * cm
    x0 = X_COL_IZQ + 0.25 * cm

    campo(pdf, x0, yy, "Marca:", catalogos["marca"])
    campo(pdf, X_COL_IZQ + 9 * cm, yy, "Modelo:", catalogos["modelo"])
    yy -= ALTO_RENGLON

    campo(pdf, x0, yy, "Placas:", boleta.placas)
    campo(pdf, X_COL_IZQ + 9 * cm, yy, "Estado:", catalogos["estado_vehiculo"])
    yy -= ALTO_RENGLON

    campo(pdf, x0, yy, "Tipo:", catalogos["tipo"])
    campo(pdf, X_COL_IZQ + 9 * cm, yy, "Año:", str(boleta.anio) if boleta.anio else "")
    yy -= ALTO_RENGLON

    campo(pdf, x0, yy, "No. Motor:", boleta.numero_motor)
    campo(pdf, X_COL_IZQ + 9 * cm, yy, "Color:", boleta.color)
    yy -= ALTO_RENGLON

    campo(pdf, x0, yy, "No. Serie:", boleta.numero_serie)
    yy -= ALTO_RENGLON * 0.8

    # Línea divisoria interna + Garantía
    pdf.setStrokeColor(COLOR_GRIS)
    pdf.line(x0, yy, X_COL_IZQ + ANCHO_COL_IZQ - 0.25 * cm, yy)
    pdf.setFont(FUENTE_BOLD, 7.5)
    pdf.setFillColor(COLOR_NEGRO)
    pdf.drawString(x0, yy, "Garantía:")
    yy -= ALTO_RENGLON

    campo(
    pdf,
    x0,
    yy,
    "Licencia No.:",
    getattr(boleta, "licencia", "")
    )

    campo(
        pdf,
        X_COL_IZQ + 8 * cm,
        yy,
        "Tarjeta circ.:",
        getattr(boleta, "tarjeta_circulacion", "")
    )

    yy -= ALTO_RENGLON

    campo(
        pdf,
        x0,
        yy,
        "Placas:",
        getattr(boleta, "placas_garantia", "")
    )

    campo(
        pdf,
        X_COL_IZQ + 8 * cm,
        yy,
        "Año:",
        str(boleta.anio) if boleta.anio else ""
    )



    y_bottom = y_contenido - alto_cuerpo
    cerrar_seccion(pdf, X_COL_IZQ, y_contenido, ANCHO_COL_IZQ, y_bottom)
    return y_bottom


# ==========================
# OBSERVACIONES + FIRMA CONDUCTOR (col. izquierda, pie)
# ==========================

def dibujar_firma(pdf, firma_base64, x, y, ancho=4*cm, alto=1.4*cm):

    if not firma_base64:
        return

    try:

        if "," in firma_base64:
            firma_base64 = firma_base64.split(",")[1]

        imagen = ImageReader(
            io.BytesIO(
                base64.b64decode(firma_base64)
            )
        )

        pdf.drawImage(
            imagen,
            x,
            y,
            width=ancho,
            height=alto,
            preserveAspectRatio=True,
            mask="auto"
        )

    except Exception as e:
        print("Error firma:", e)

def dibujar_observaciones_y_firma_conductor(pdf, boleta, y_top):
    alto_cuerpo = 1.3 * cm
    y_contenido = iniciar_seccion(pdf, X_COL_IZQ, y_top, ANCHO_COL_IZQ, "OBSERVACIONES")
    yy = y_contenido - 0.5 * cm
    x0 = X_COL_IZQ + 0.25 * cm

    lineas = wrap_text(pdf, boleta.observaciones or "", FUENTE, TAM_TEXTO, ANCHO_COL_IZQ - 0.5 * cm)
    for linea in lineas[:2]:
        pdf.setFont(FUENTE, TAM_TEXTO)
        pdf.setFillColor(COLOR_NEGRO)
        pdf.drawString(x0, yy, linea)
        yy -= 0.45 * cm

    y_bottom = y_contenido - alto_cuerpo
    cerrar_seccion(pdf, X_COL_IZQ, y_contenido, ANCHO_COL_IZQ, y_bottom)

    # Firma del conductor debajo del recuadro
    y_firma = y_bottom - 3 * cm

    x_inicio = X_COL_IZQ + 1 * cm
    x_fin = X_COL_IZQ + 5 * cm

    dibujar_firma(
        pdf,
        boleta.firma_conductor,
        x_inicio,
        y_firma + 0.35 * cm
    )

    pdf.setStrokeColor(COLOR_NEGRO)

    pdf.line(
        x_inicio,
        y_firma + 0.3 * cm,
        x_fin,
        y_firma + 0.3 * cm
    )

    pdf.setFont(FUENTE, 9)
    pdf.setFillColor(COLOR_NEGRO)

    pdf.drawCentredString(
        (x_inicio + x_fin) / 2,
        y_firma,
        "Firma del Conductor"
    )

    pdf.drawCentredString(
        (x_inicio + x_fin) / 2,
        y_firma - 0.4 * cm,
        boleta.conductor_nombre or ""
    )

    return y_firma


# ==========================
# MOTIVO / FUNDAMENTO / FORMULÓ (col. derecha)
# ==========================

def dibujar_motivo_y_formulo(pdf, boleta, catalogos, y_top,oficial_nombre):
    ancho_interior = ANCHO_COL_DER - 0.5 * cm

    # --- Motivo de la infracción y fundamento ---
    alto_motivo = 7.5 * cm
    y_contenido = iniciar_seccion(pdf, X_COL_DER, y_top, ANCHO_COL_DER, "MOTIVO DE LA INFRACCIÓN Y FUNDAMENTO")
    yy = y_contenido - 0.55 * cm
    x0 = X_COL_DER + 0.25 * cm

    motivos = catalogos.get("motivos") or []

    if motivos:
        bloques = []
        for index, motivo in enumerate(motivos, start=1):
            bloque = f"{index}. {motivo.descripcion}"
            bloque += f"\nFuente de ingreso: {motivo.fuente_ingreso}"
            bloque += f"\nArtículo: {motivo.articulo}"

            if motivo.fraccion:
                bloque += f"\nFracción: {motivo.fraccion}"

            if motivo.inciso:
                bloque += f"\nInciso: {motivo.inciso}"

            if motivo.numeral:
                bloque += f"\nNumeral: {motivo.numeral}"

            if motivo.fundamento:
                bloque += f"\nFundamento: {motivo.fundamento}"

            bloques.append(bloque)

        texto_motivo = "\n\n".join(bloques)
    else:
        texto_motivo = "Sin motivo especificado"

    pdf.setFont(FUENTE, TAM_TEXTO)
    pdf.setFillColor(COLOR_NEGRO)

    for bloque in texto_motivo.split("\n"):

        for linea in wrap_text(
            pdf,
            bloque,
            FUENTE,
            TAM_TEXTO,
            ancho_interior
        ):
            pdf.drawString(x0, yy, linea)
            yy -= 0.42 * cm

        yy -= 0.15 * cm

    y_bottom_motivo = y_contenido - alto_motivo
    cerrar_seccion(pdf, X_COL_DER, y_contenido, ANCHO_COL_DER, y_bottom_motivo)

    # --- Número de parte de accidente / tipo ---
    y = y_bottom_motivo - 0.3 * cm
    alto_parte = 1.6 * cm
    y_contenido = iniciar_seccion(pdf, X_COL_DER, y, ANCHO_COL_DER, "NÚMERO DE PARTE DE ACCIDENTE")
    yy = y_contenido - 0.5 * cm
    campo(pdf, x0, yy, "Número:", boleta.numero_parte or "-")
    yy -= ALTO_RENGLON
    campo(pdf, x0, yy, "Tipo:", boleta.tipo_accidente or "-")
    y_bottom_parte = y_contenido - alto_parte
    cerrar_seccion(pdf, X_COL_DER, y_contenido, ANCHO_COL_DER, y_bottom_parte)

    # --- Formuló: nombre y firma del oficial ---
    y = y_bottom_parte - 0.3 * cm
    alto_formulo = 3.8 * cm
    y_contenido = iniciar_seccion(pdf, X_COL_DER, y, ANCHO_COL_DER, "FORMULÓ: NOMBRE Y FIRMA")
    yy = y_contenido - 0.5 * cm
    campo(pdf, x0, yy, "Oficial:", oficial_nombre or "")
    yy -= ALTO_RENGLON
    campo(pdf, x0, yy, "No. Empleado:", boleta.empleado_id or "")
    yy -= ALTO_RENGLON
    campo(pdf, x0, yy, "No. Patrulla:", boleta.patrulla or "")
    
    yy -= 3.5 * cm


# Firma del oficial
    x_inicio_firma = X_COL_DER - 5.5 * cm
    x_fin_firma = X_COL_DER - 2.5 * cm


    dibujar_firma(
        pdf,
        boleta.firma_oficial,
        x_inicio_firma,
        yy + 0.35 * cm
    )


    pdf.setStrokeColor(COLOR_NEGRO)

    pdf.line(
        x_inicio_firma,
        yy + 0.3 * cm,
        x_fin_firma,
        yy + 0.3 * cm
    )


    pdf.setFont(FUENTE, 9)
    pdf.setFillColor(COLOR_NEGRO)

    pdf.drawCentredString(
        (x_inicio_firma + x_fin_firma) / 2,
        yy - 0.05 * cm,
        "Firma del Oficial"
    )

    pdf.drawCentredString(
        (x_inicio_firma + x_fin_firma) / 2,
        yy - 0.45 * cm,
        oficial_nombre or ""
    )

    y_bottom_formulo = y_contenido - alto_formulo
    cerrar_seccion(pdf, X_COL_DER, y_contenido, ANCHO_COL_DER, y_bottom_formulo)

    # --- Nota legal ---
    nota = (
        "Nota: El infractor tendrá un plazo de noventa días naturales a partir de "
        "la fecha de emisión de la boleta para realizar el pago, sujeto a un "
        "descuento del 50% dentro de los primeros diez días hábiles (aplican "
        "restricciones). Vencido el plazo, deberá cubrir los demás créditos "
        "fiscales y actualizaciones conforme al Código Fiscal del Estado de Querétaro."
    )
    y = y_bottom_formulo - 0.4 * cm
    pdf.setFont(FUENTE, 7.5)
    pdf.setFillColor(colors.grey)
    for linea in wrap_text(pdf, nota, FUENTE, 7.5, ancho_interior):
        pdf.drawString(x0, y, linea)
        y -= 0.32 * cm

    return y


# ==========================
# QR
# ==========================

def crear_qr(pdf, boleta, x, y, tamano=1.8 * cm):
    datos = f"Folio: {boleta.folio}\nFecha: {boleta.fecha}\nPlacas: {boleta.placas}"
    qr = qrcode.make(datos)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        qr.save(tmp.name)
        pdf.drawImage(tmp.name, x, y, width=tamano, height=tamano)
    Path(tmp.name).unlink(missing_ok=True)


# ==========================
# PIE DE PÁGINA
# ==========================

def dibujar_pie_pagina(pdf):
    pdf.setStrokeColor(COLOR_AZUL)
    pdf.setLineWidth(1)
    pdf.line(MARGEN_X, 0.8 * cm, ANCHO - MARGEN_X, 0.8 * cm)
    pdf.setFillColor(COLOR_NEGRO)
    pdf.setFont(FUENTE, 8)
    pdf.drawString(MARGEN_X, 0.4 * cm, "Secretaría de Movilidad - Municipio de El Marqués")
    pdf.drawRightString(ANCHO - MARGEN_X, 0.4 * cm, "Boleta oficial de infracción")