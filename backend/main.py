from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1 import router as api_router
from app.db.database import engine, Base
from app.models import user, business

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print(f"ServiciosBogota iniciando en modo {settings.APP_ENV}")
    yield
    print("Servidor detenido")

app = FastAPI(
    title=settings.APP_NAME,
    description="API del directorio de servicios locales para Bogota",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://serviciosbogota.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}