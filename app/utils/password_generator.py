import secrets
import string


def generar_password_temporal():

    caracteres = (
        string.ascii_letters +
        string.digits
    )

    password = ''.join(
        secrets.choice(caracteres)
        for _ in range(10)
    )

    return password