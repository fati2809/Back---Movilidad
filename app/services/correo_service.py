import random


codigos = {}


def generar_codigo():
    return str(random.randint(100000,999999))


def guardar_codigo(correo:str):

    codigo = generar_codigo()

    codigos[correo] = codigo

    return codigo


def verificar_codigo(correo:str,codigo:str):

    codigo_guardado = codigos.get(correo)

    if not codigo_guardado:
        return False

    return codigo_guardado == codigo