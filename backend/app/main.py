from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import orders, products
from app import models

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orders API - Actividad No.5",
    description="API REST para gestión de pedidos",
    version="1.0.0"
)

# ========== CONFIGURACIÓN CORS (NECESARIO PARA FRONTEND) ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://actividad5-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "message": "API funcionando correctamente",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    return {
        "message": "Bienvenido a Orders API",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health"
    }

# Incluir routers
app.include_router(orders.router, prefix="/api/v1", tags=["orders"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])