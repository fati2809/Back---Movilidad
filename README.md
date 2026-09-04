## Correo en producción

El envío usa la API HTTPS de Resend, por lo que no depende de que el servidor
público permita conexiones SMTP salientes.

Configura estas variables de entorno en el servidor:

```env
RESEND_API_KEY=re_xxxxxxxxx
RESEND_FROM=Movilidad <correo@tu-dominio-verificado.com>
```

En Resend debes verificar el dominio del remitente antes de usarlo.

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