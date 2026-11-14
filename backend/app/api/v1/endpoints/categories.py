from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.business import LOCALIDADES_BOGOTA, Business, BusinessStatus
from app.models.category import Category
from app.models.review import Review
from app.schemas.business import CategoryOut

router = APIRouter(tags=["Catálogos"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return (
        db.query(Category)
        .filter(Category.is_active.is_(True))
        .order_by(Category.sort_order, Category.name)
        .all()
    )


@router.get("/localidades", response_model=list[str])
def list_localidades():
    return LOCALIDADES_BOGOTA


@router.get("/stats")
def public_stats(db: Session = Depends(get_db)):
    """Cifras reales del directorio para mostrar en el sitio."""
    active = db.query(Business).filter(Business.status == BusinessStatus.active)
    return {
        "businesses": active.count(),
        "categories": db.query(Category).filter(Category.is_active.is_(True)).count(),
        "reviews": db.query(Review).filter(Review.is_approved.is_(True)).count(),
        "localidades": active.with_entities(func.count(func.distinct(Business.localidad))).scalar() or 0,
    }
