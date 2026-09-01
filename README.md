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