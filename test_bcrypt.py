from app.core.security import verify_password


hash_db = "$2b$12$kBkzkfMhSe4buweg/6EUAedu0fOUvqlQViK2bc/tmggpija8u6ESy"


resultado = verify_password(
    "Hola.123",
    hash_db
)


print(resultado)