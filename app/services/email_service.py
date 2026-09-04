import base64
import os
from email.utils import parseaddr
from pathlib import Path

import httpx
from dotenv import load_dotenv


BREVO_URL = "https://api.brevo.com/v3/smtp/email"
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


async def _enviar_correo(
    destinatario,
    asunto,
    cuerpo,
    archivo=None
):
    api_key = os.getenv("BREVO_API_KEY")
    remitente = os.getenv("BREVO_FROM")

    if not api_key or not remitente:
        raise RuntimeError(
            "Configura BREVO_API_KEY y BREVO_FROM en las variables de entorno"
        )

    nombre_remitente, correo_remitente = parseaddr(remitente)
    if not correo_remitente:
        correo_remitente = remitente

    datos = {
        "sender": {"email": correo_remitente},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "textContent": cuerpo,
    }

    if nombre_remitente:
        datos["sender"]["name"] = nombre_remitente

    if archivo:
        ruta = Path(archivo)
        datos["attachment"] = [{
            "content": base64.b64encode(ruta.read_bytes()).decode("ascii"),
            "name": ruta.name,
        }]

    async with httpx.AsyncClient(timeout=30) as cliente:
        respuesta = await cliente.post(
            BREVO_URL,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
            },
            json=datos,
        )

    if respuesta.is_error:
        raise RuntimeError(
            f"Brevo rechazó el correo ({respuesta.status_code}): {respuesta.text}"
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