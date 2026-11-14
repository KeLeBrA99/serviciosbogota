"""Subida de imágenes a Cloudinary."""
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile

from app.core.config import settings

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


def upload_image(file: UploadFile, folder: str) -> str:
    if not settings.cloudinary_enabled:
        raise HTTPException(
            status_code=503,
            detail="La subida de imágenes aún no está configurada (faltan las credenciales de Cloudinary).",
        )
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usa JPG, PNG o WEBP.")
    content = file.file.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="La imagen supera el máximo de 5 MB.")
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    try:
        result = cloudinary.uploader.upload(
            content,
            folder=f"serviciosbogota/{folder}",
            resource_type="image",
            transformation=[{"width": 1600, "height": 1600, "crop": "limit", "quality": "auto"}],
        )
    except Exception:
        raise HTTPException(status_code=502, detail="No se pudo subir la imagen. Intenta de nuevo.")
    return result["secure_url"]
