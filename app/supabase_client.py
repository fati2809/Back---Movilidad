import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno del archivo .env
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan las variables de entorno SUPABASE_URL o SUPABASE_KEY")

# Instanciar el cliente
supabase: Client = create_client(url, key)

# Ejemplo de uso:
# response = supabase.table("tu_tabla").select("*").execute()
