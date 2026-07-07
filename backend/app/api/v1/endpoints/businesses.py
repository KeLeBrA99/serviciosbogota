from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessOut, PaginatedBusinesses
from app.services.business_service import (
    get_businesses, get_business_by_slug, create_business, update_business
)

router = APIRouter(prefix="/businesses", tags=["Negocios"])


@router.get("/", response_model=PaginatedBusinesses)
def list_businesses(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    category: Optional[str] = Query(None),
    localidad: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    featured: bool = Query(False),
    db: Session = Depends(get_db),
):
    return get_businesses(db, page, per_page, category, localidad, search, featured)


@router.get("/my", response_model=list[BusinessOut])
def my_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.business import Business
    from sqlalchemy.orm import joinedload
    return (
        db.query(Business)
        .options(joinedload(Business.category), joinedload(Business.subscription))
        .filter(Business.owner_id == current_user.id)
        .all()
    )


@router.post("/", response_model=BusinessOut, status_code=201)
def create(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_business(db, data, current_user)


@router.get("/{slug}", response_model=BusinessOut)
def get_by_slug(slug: str, db: Session = Depends(get_db)):
    return get_business_by_slug(db, slug)


@router.put("/{business_id}", response_model=BusinessOut)
def update(
    business_id: int,
    data: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_business(db, business_id, data, current_user)
