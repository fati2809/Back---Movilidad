from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models

from app.routes.auth import router as auth_router
from app.routes import catalogos_routes
from app.routes import boleta_routes
from app.routes import correo_routes
from app.routes.user_routes import router as user_router
from app.routes import rol_routes
from app.routes import reportes


app = FastAPI(
    title="Sistema de Movilidad",
    version="1.0.0"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =====================================================
# LOGIN
# =====================================================

app.include_router(
    auth_router
)


# =====================================================
# CATALOGOS
# =====================================================

app.include_router(
    catalogos_routes.router
)


# =====================================================
# BOLETAS
# =====================================================

app.include_router(
    boleta_routes.router
)


# =====================================================
# CORREO
# =====================================================

app.include_router(
    correo_routes.router
)


# =====================================================
# USUARIOS
# =====================================================

app.include_router(
    user_router
)


# =====================================================
# ROLES
# =====================================================

app.include_router(
    rol_routes.router
)


# =====================================================
# REPORTES
# =====================================================

app.include_router(
    reportes.router
)


# =====================================================
# INICIO
# =====================================================

@app.get("/")
def home():

    return {
        "mensaje": "API funcionando correctamente"
    }