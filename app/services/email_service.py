from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig
)


conf = ConnectionConfig(
    MAIL_USERNAME="lopez.uribe.fatima@gmail.com",
    MAIL_PASSWORD="ypqf spfs xrim czme",
    MAIL_FROM="lopez.uribe.fatima@gmail.com",
    MAIL_FROM_NAME="Movilidad",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)


# =====================================================
# ENVIAR BOLETA PDF
# =====================================================

async def enviar_pdf_correo(
    correo,
    archivo
):

    mensaje = MessageSchema(

        subject="Boleta de infracción",

        recipients=[
            correo
        ],

        body="""
        Se adjunta la boleta de infracción generada.
        """,

        attachments=[
            archivo
        ],

        subtype="plain"
    )

    fm = FastMail(conf)

    await fm.send_message(
        mensaje
    )


# =====================================================
# ENVIAR CÓDIGO OTP
# =====================================================

async def enviar_codigo_correo(
    correo,
    codigo
):

    mensaje = MessageSchema(

        subject="Código de verificación",

        recipients=[
            correo
        ],

        body=f"""
        Código de verificación de Movilidad:

        {codigo}


        Si usted no solicitó este código ignore este mensaje.
        """,

        subtype="plain"
    )

    fm = FastMail(conf)

    await fm.send_message(
        mensaje
    )


# =====================================================
# ENVIAR CONTRASEÑA TEMPORAL - CREACIÓN DE USUARIO
# =====================================================

async def enviar_correo_usuario(
    correo,
    password
):

    mensaje = MessageSchema(

        subject="Cuenta creada - Movilidad",

        recipients=[
            correo
        ],

        body=f"""
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

        subtype="plain"
    )

    fm = FastMail(conf)

    await fm.send_message(
        mensaje
    )


# =====================================================
# ENVIAR CORREO DE RECUPERACIÓN DE CONTRASEÑA
# =====================================================

async def enviar_correo_recuperacion(
    correo,
    password
):

    mensaje = MessageSchema(

        subject="Recuperación de contraseña - Movilidad",

        recipients=[
            correo
        ],

        body=f"""
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

        subtype="plain"
    )

    fm = FastMail(conf)

    await fm.send_message(
        mensaje
    )