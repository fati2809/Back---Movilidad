from fastapi import APIRouter, HTTPException

from app.services.correo_service import (
    guardar_codigo,
    verificar_codigo
)

from app.services.email_service import (
    enviar_codigo_correo
)


router = APIRouter(
    prefix="/correo",
    tags=["Correo"]
)


# =================================
# ENVIAR CÓDIGO AL CORREO
# =================================

@router.post("/enviar-codigo")
async def enviar_codigo(data: dict):

    correo = data.get("correo")


    if not correo:
        raise HTTPException(
            status_code=400,
            detail="Correo requerido"
        )


    codigo = guardar_codigo(correo)


    await enviar_codigo_correo(
        correo,
        codigo
    )


    return {
        "mensaje": "Código enviado"
    }



# =================================
# VERIFICAR CÓDIGO
# =================================

@router.post("/verificar-codigo")
async def validar_codigo(data: dict):

    correo = data.get("correo")
    codigo = data.get("codigo")


    if not correo or not codigo:
        raise HTTPException(
            status_code=400,
            detail="Correo y código requeridos"
        )


    correcto = verificar_codigo(
        correo,
        codigo
    )


    if not correcto:
        raise HTTPException(
            status_code=400,
            detail="Código incorrecto"
        )


    return {
        "verificado": True
    }