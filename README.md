## Correo en producción

El envío usa la API HTTPS de SendGrid, por lo que no depende de que el servidor
público permita conexiones SMTP salientes.

Configura estas variables de entorno en el servidor:

```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxx
SENDGRID_FROM=Movilidad <correo@dominio-verificado.com>
```

En SendGrid debes verificar el remitente o el dominio antes de usarlo.

## Autenticación

### POST /auth/login

Ejemplo de solicitud

```json
{
    "email": "admin@correo.com",
    "password": "123456"
}
```

Respuesta

```json
{
    "success": true,
    "usuario": {
        "id": 1,
        "nombre": "Administrador",
        "email": "admin@correo.com",
        "rol": "Administrador"
    }
}
```