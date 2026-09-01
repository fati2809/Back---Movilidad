from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

PLACEHOLDER_VALUES = (
    "db.tu_proyecto_ref.supabase.co",
    "tu_password",
    "tu_proyecto_ref",
    "postgresql+psycopg2://postgres:tu_password@",
    "postgresql+psycopg2://postgres:TU_PASSWORD@",
)

if not DATABASE_URL or any(value in DATABASE_URL for value in PLACEHOLDER_VALUES):
    raise RuntimeError(
        "DATABASE_URL no está configurada para Supabase. "
        "Copia la cadena de conexión de PostgreSQL desde el panel de Supabase y guárdala en Back/.env."
    )

if "pgbouncer=true" in DATABASE_URL.lower():
    DATABASE_URL = DATABASE_URL.split("?", 1)[0]

engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}

if DATABASE_URL.startswith("postgresql"):
    engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()