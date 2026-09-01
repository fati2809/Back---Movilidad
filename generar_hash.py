import bcrypt


password = "Hola.123"


hashed = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
)


print("Password:")
print(password)

print("\nHash:")
print(hashed.decode("utf-8"))