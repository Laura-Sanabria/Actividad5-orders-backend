# Actividad5-Orders Platform

API REST + Frontend para gestión de pedidos - Actividad No.5 SENA

## Tecnologías
- Backend: Python + FastAPI + SQLAlchemy
- Frontend: Next.js + Tailwind + DevExtreme
- Despliegue: Render.com

## API Endpoints
- Health: `/api/v1/health`
- Products: `/api/v1/products`
- Orders: `/api/v1/orders`

## Cómo ejecutar localmente

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload