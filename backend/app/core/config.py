from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# Orígenes que siempre se permiten, además de los configurados por entorno.
DEFAULT_CORS_ORIGINS = [
    "https://serviciosbogota.vercel.app",
    "http://localhost:5173",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # App
    APP_NAME: str = "ServiciosBogotá"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"

    # Base de datos
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Administrador inicial (opcional). Si ambos están definidos, se crea al arrancar.
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""

    # Wompi
    WOMPI_PUBLIC_KEY: str = ""
    WOMPI_PRIVATE_KEY: str = ""
    WOMPI_EVENTS_SECRET: str = ""
    WOMPI_INTEGRITY_SECRET: str = ""
    WOMPI_BASE_URL: str = "https://sandbox.wompi.co/v1"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    @property
    def cors_origins(self) -> List[str]:
        origins = [*DEFAULT_CORS_ORIGINS, *self.CORS_ORIGINS, self.FRONTEND_URL]
        return sorted({o.rstrip("/") for o in origins if o})

    @property
    def wompi_enabled(self) -> bool:
        return bool(self.WOMPI_PUBLIC_KEY) and "xxxx" not in self.WOMPI_PUBLIC_KEY

    @property
    def cloudinary_enabled(self) -> bool:
        return (
            bool(self.CLOUDINARY_CLOUD_NAME and self.CLOUDINARY_API_KEY and self.CLOUDINARY_API_SECRET)
            and not self.CLOUDINARY_CLOUD_NAME.startswith("tu_")
        )


settings = Settings()
