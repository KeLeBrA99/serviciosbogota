import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.db.database import SessionLocal
from app.db.init_db import seed_admin, seed_categories
from app.db.migrations import run_migrations
from app.services.subscription_service import run_subscription_sweep

logger = logging.getLogger("serviciosbogota")
SWEEP_INTERVAL_SECONDS = 3600


def _sweep_subscriptions() -> None:
    db = SessionLocal()
    try:
        run_subscription_sweep(db)
    finally:
        db.close()


async def _periodic_sweep() -> None:
    """Cada hora vence planes y envía recordatorios, sin depender de un cron externo."""
    while True:
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)
        try:
            await asyncio.to_thread(_sweep_subscriptions)
        except Exception:
            logger.exception("Falló el barrido de suscripciones")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_admin(db)
        run_subscription_sweep(db)
    finally:
        db.close()
    sweep_task = asyncio.create_task(_periodic_sweep())
    print(f"ServiciosBogota iniciando en modo {settings.APP_ENV}")
    yield
    sweep_task.cancel()
    print("Servidor detenido")


app = FastAPI(
    title=settings.APP_NAME,
    description="API del directorio de servicios locales para Bogota",
    version="1.2.0",
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
