from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_optional_user, get_owned_business
from app.db.database import get_db
from app.models.user import User
from app.schemas.business import (
    BusinessCreate,
    BusinessOut,
    BusinessUpdate,
    PaginatedBusinesses,
    PhotoDelete,
)
from app.services.business_service import (
    create_business,
    delete_business,
    get_business_by_slug,
    get_businesses,
    get_my_businesses,
    photos_limit,
    update_business,
)
from app.services.upload_service import upload_image

# Las rutas raíz usan "" (sin barra final) para que /businesses no responda con
# una redirección 307, que detrás de un proxy puede degradar HTTPS a HTTP.
router = APIRouter(prefix="/businesses", tags=["Negocios"])


@router.get("", response_model=PaginatedBusinesses)
def list_businesses(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    category: Optional[str] = Query(None),
    localidad: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    featured: bool = Query(False),
    sort: Literal["relevance", "rating", "recent"] = Query("relevance"),
    db: Session = Depends(get_db),
):
    return get_businesses(db, page, per_page, category, localidad, search, featured, sort)


@router.get("/my", response_model=list[BusinessOut])
def my_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_businesses(db, current_user)


@router.post("", response_model=BusinessOut, status_code=201)
def create(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_business(db, data, current_user)


@router.get("/{slug}", response_model=BusinessOut)
def get_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    viewer: Optional[User] = Depends(get_optional_user),
):
    return get_business_by_slug(db, slug, viewer)


@router.put("/{business_id}", response_model=BusinessOut)
def update(
    business_id: int,
    data: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owned_business(db, business_id, current_user)
    return update_business(db, business, data)


@router.delete("/{business_id}", status_code=204)
def delete(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owned_business(db, business_id, current_user)
    delete_business(db, business)


# ── Imágenes ──

@router.post("/{business_id}/logo", response_model=BusinessOut)
def upload_logo(
    business_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owned_business(db, business_id, current_user)
    business.logo_url = upload_image(file, f"negocios/{business.id}")
    db.commit()
    db.refresh(business)
    return business


@router.post("/{business_id}/cover", response_model=BusinessOut)
def upload_cover(
    business_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owned_business(db, business_id, current_user)
    business.cover_url = upload_image(file, f"negocios/{business.id}")
    db.commit()
    db.refresh(business)
    return business


@router.post("/{business_id}/photos", response_model=BusinessOut)
def upload_photo(
    business_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owned_business(db, business_id, current_user)
    photos = list(business.photos or [])
    limit = photos_limit(business)
    if len(photos) >= limit:
        raise HTTPException(
            status_code=400,
            detail=f"Tu plan permite hasta {limit} fotos. Pásate a Premium para subir más.",
        )
    photos.append(upload_image(file, f"negocios/{business.id}"))
    business.photos = photos  # se reasigna la lista para que SQLAlchemy detecte el cambio
    db.commit()
    db.refresh(business)
    return business


@router.delete("/{business_id}/photos", response_model=BusinessOut)
def delete_photo(
    business_id: int,
    data: PhotoDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owned_business(db, business_id, current_user)
    business.photos = [url for url in (business.photos or []) if url != data.url]
    db.commit()
    db.refresh(business)
    return business
