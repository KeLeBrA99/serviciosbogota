from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.db.database import SessionLocal
from app.db.init_db import create_tables, seed_admin, seed_categories
from app.services.subscription_service import expire_subscriptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_admin(db)
        expire_subscriptions(db)
    finally:
        db.close()
    print(f"ServiciosBogota iniciando en modo {settings.APP_ENV}")
    yield
    print("Servidor detenido")


app = FastAPI(
    title=settings.APP_NAME,
    description="API del directorio de servicios locales para Bogota",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intenta de nuevo en unos minutos."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
