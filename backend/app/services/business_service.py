import re
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from app.models.business import Business, BusinessStatus
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessUpdate


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[áàä]', 'a', text)
    text = re.sub(r'[éèë]', 'e', text)
    text = re.sub(r'[íìï]', 'i', text)
    text = re.sub(r'[óòö]', 'o', text)
    text = re.sub(r'[úùü]', 'u', text)
    text = re.sub(r'ñ', 'n', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text)


def unique_slug(db: Session, base: str) -> str:
    slug = slugify(base)
    counter = 0
    candidate = slug
    while db.query(Business).filter(Business.slug == candidate).first():
        counter += 1
        candidate = f"{slug}-{counter}"
    return candidate


def get_businesses(
    db: Session,
    page: int = 1,
    per_page: int = 12,
    category_slug: Optional[str] = None,
    localidad: Optional[str] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
) -> dict:
    query = (
        db.query(Business)
        .options(
            joinedload(Business.category),
            joinedload(Business.subscription),
        )
        .filter(Business.status == BusinessStatus.active)
    )

    if category_slug:
        query = query.join(Business.category).filter(
            Business.category.has(slug=category_slug)
        )
    if localidad:
        query = query.filter(Business.localidad == localidad)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Business.name.ilike(term),
                Business.description.ilike(term),
                Business.short_description.ilike(term),
            )
        )
    if featured_only:
        query = query.filter(Business.is_featured == True)

      # Premium primero, luego por rating
    query = query.outerjoin(Business.subscription).order_by(
        Business.is_featured.desc(),
        Business.rating_avg.desc(),
    )

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": -(-total // per_page),
        "per_page": per_page,
    }


def get_business_by_slug(db: Session, slug: str) -> Business:
    business = (
        db.query(Business)
        .options(
            joinedload(Business.category),
            joinedload(Business.subscription),
            joinedload(Business.reviews),
        )
        .filter(Business.slug == slug, Business.status == BusinessStatus.active)
        .first()
    )
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    # Incrementar vistas
    business.view_count += 1
    db.commit()
    return business


def create_business(db: Session, data: BusinessCreate, owner: User) -> Business:
    slug = unique_slug(db, data.name)
    business = Business(
    owner_id=owner.id,
    slug=slug,
    status=BusinessStatus.active,
    **data.model_dump(),
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def update_business(db: Session, business_id: int, data: BusinessUpdate, owner: User) -> Business:
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == owner.id,
    ).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(business, field, value)
    db.commit()
    db.refresh(business)
    return business


def recalculate_rating(db: Session, business_id: int):
    from app.models.review import Review
    result = db.query(
        func.avg(Review.rating).label("avg"),
        func.count(Review.id).label("count"),
    ).filter(
        Review.business_id == business_id,
        Review.is_approved == True,
    ).first()
    db.query(Business).filter(Business.id == business_id).update({
        "rating_avg": round(result.avg or 0, 1),
        "rating_count": result.count or 0,
    })
    db.commit()
