import base64
import os
from email.utils import parseaddr
from pathlib import Path

import httpx
from dotenv import load_dotenv


SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


async def _enviar_correo(
    destinatario,
    asunto,
    cuerpo,
    archivo=None
):
    api_key = os.getenv("SENDGRID_API_KEY")
    remitente = os.getenv("SENDGRID_FROM")

    if not api_key or not remitente:
        raise RuntimeError(
            "Configura SENDGRID_API_KEY y SENDGRID_FROM en las variables de entorno"
        )

    nombre_remitente, correo_remitente = parseaddr(remitente)
    if not correo_remitente:
        correo_remitente = remitente

    datos = {
        "personalizations": [{
            "to": [{"email": destinatario}],
        }],
        "from": {"email": correo_remitente},
        "subject": asunto,
        "content": [{"type": "text/plain", "value": cuerpo}],
    }

    if nombre_remitente:
        datos["from"]["name"] = nombre_remitente

    if archivo:
        ruta = Path(archivo)
        datos["attachments"] = [{
            "content": base64.b64encode(ruta.read_bytes()).decode("ascii"),
            "filename": ruta.name,
            "type": "application/pdf",
            "disposition": "attachment",
        }]

    async with httpx.AsyncClient(timeout=30) as cliente:
        respuesta = await cliente.post(
            SENDGRID_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=datos,
        )

    if respuesta.is_error:
        raise RuntimeError(
            f"SendGrid rechazó el correo ({respuesta.status_code}): {respuesta.text}"
        )


# =====================================================
# ENVIAR BOLETA PDF
# =====================================================

async def enviar_pdf_correo(
    correo,
    archivo
):
    await _enviar_correo(
        correo,
        "Boleta de infracción",
        "Se adjunta la boleta de infracción generada.",
        archivo,
    )


# =====================================================
# ENVIAR CÓDIGO OTP
# =====================================================

async def enviar_codigo_correo(
    correo,
    codigo
):
    await _enviar_correo(
        correo,
        "Código de verificación",
        f"""
        Código de verificación de Movilidad:

        {codigo}


        Si usted no solicitó este código ignore este mensaje.
        """,
    )


# =====================================================
# ENVIAR CONTRASEÑA TEMPORAL - CREACIÓN DE USUARIO
# =====================================================

async def enviar_correo_usuario(
    correo,
    password
):
    await _enviar_correo(
        correo,
        "Cuenta creada - Movilidad",
        f"""
        Bienvenido al sistema de Movilidad.

        Tu cuenta fue creada correctamente.


        Usuario:

        {correo}


        Contraseña temporal:

        {password}


        IMPORTANTE:

        Al iniciar sesión por primera vez
        deberás cambiar esta contraseña.


        Si usted no solicitó esta cuenta,
        contacte al administrador.
        """,
    )


# =====================================================
# ENVIAR CORREO DE RECUPERACIÓN DE CONTRASEÑA
# =====================================================

async def enviar_correo_recuperacion(
    correo,
    password
):
    await _enviar_correo(
        correo,
        "Recuperación de contraseña - Movilidad",
        f"""
        Hola,

        Se ha solicitado la recuperación de contraseña
        de tu cuenta del sistema de Movilidad.


        Tu nueva contraseña temporal es:

        {password}


        IMPORTANTE:

        Inicia sesión con esta contraseña y cámbiala
        inmediatamente por una nueva.


        Si usted no solicitó recuperar su contraseña,
        contacte al administrador.
        """,
    )