from fastapi import FastAPI
from app.database import engine, Base
from app.routers import orders, products
from app.load_endpoint import router as load_router  # ← LÍNEA NUEVA (al inicio)
from app import models

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orders API - Actividad No.5",
    description="API REST para gestión de pedidos",
    version="1.0.0"
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

# ========== INCLUIR ROUTERS ==========
app.include_router(orders.router, prefix="/api/v1", tags=["orders"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(load_router, prefix="/api/v1", tags=["admin"])  # ← LÍNEA NUEVA (al final)