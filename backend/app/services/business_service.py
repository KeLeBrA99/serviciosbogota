import re
import unicodedata
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.business import Business, BusinessStatus
from app.models.category import Category
from app.models.contact import ContactRequest
from app.models.event import BusinessEvent
from app.models.review import Review
from app.models.subscription import PLAN_FEATURES, PlanType, Subscription, SubscriptionStatus
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessUpdate
from app.services.subscription_service import _utcnow, expire_subscriptions_if_due

FREE_PHOTOS_LIMIT = PLAN_FEATURES[PlanType.basic]["photos_limit"]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower().strip())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-") or "negocio"


def unique_slug(db: Session, base: str) -> str:
    slug = slugify(base)[:180]
    counter = 0
    candidate = slug
    while db.query(Business).filter(Business.slug == candidate).first():
        counter += 1
        candidate = f"{slug}-{counter}"
    return candidate


def _ensure_category(db: Session, category_id: int) -> None:
    exists = db.query(Category).filter(Category.id == category_id, Category.is_active.is_(True)).first()
    if not exists:
        raise HTTPException(status_code=400, detail="La categoría seleccionada no existe")


def get_businesses(
    db: Session,
    page: int = 1,
    per_page: int = 12,
    category_slug: Optional[str] = None,
    localidad: Optional[str] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
    sort: str = "relevance",
) -> dict:
    expire_subscriptions_if_due(db)

    query = (
        db.query(Business)
        .join(Business.category)
        .options(joinedload(Business.category), joinedload(Business.subscription))
        .filter(Business.status == BusinessStatus.active)
    )

    if category_slug:
        query = query.filter(Category.slug == category_slug)
    if localidad:
        query = query.filter(Business.localidad == localidad)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Business.name.ilike(term),
                Business.description.ilike(term),
                Business.short_description.ilike(term),
                Business.neighborhood.ilike(term),
                Category.name.ilike(term),
            )
        )
    if featured_only:
        query = query.filter(Business.is_featured.is_(True))

    total = query.count()

    # Los destacados (plan Premium) siempre van primero.
    if sort == "recent":
        order = [Business.is_featured.desc(), Business.created_at.desc()]
    elif sort == "rating":
        order = [Business.is_featured.desc(), Business.rating_avg.desc(), Business.rating_count.desc()]
    else:
        order = [Business.is_featured.desc(), Business.rating_avg.desc(), Business.view_count.desc()]
    items = query.order_by(*order, Business.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": max(1, -(-total // per_page)),
        "per_page": per_page,
    }


def get_my_businesses(db: Session, owner: User) -> list[Business]:
    expire_subscriptions_if_due(db)
    return (
        db.query(Business)
        .options(joinedload(Business.category), joinedload(Business.subscription))
        .filter(Business.owner_id == owner.id)
        .order_by(Business.created_at.desc())
        .all()
    )


def get_business_by_slug(db: Session, slug: str, viewer: Optional[User] = None) -> Business:
    business = (
        db.query(Business)
        .options(joinedload(Business.category), joinedload(Business.subscription))
        .filter(Business.slug == slug)
        .first()
    )
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    is_owner = viewer is not None and (viewer.id == business.owner_id or viewer.role.value == "admin")
    if business.status != BusinessStatus.active and not is_owner:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    if not is_owner:
        # Las visitas del dueño no cuentan como vistas.
        db.query(Business).filter(Business.id == business.id).update(
            {Business.view_count: Business.view_count + 1}, synchronize_session=False
        )
        db.commit()
        db.refresh(business)
    return business


def create_business(db: Session, data: BusinessCreate, owner: User) -> Business:
    _ensure_category(db, data.category_id)
    business = Business(
        owner_id=owner.id,
        slug=unique_slug(db, data.name),
        status=BusinessStatus.active,
        photos=[],
        **data.model_dump(),
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def update_business(db: Session, business: Business, data: BusinessUpdate) -> Business:
    changes = data.model_dump(exclude_unset=True)
    if changes.get("category_id") is not None:
        _ensure_category(db, changes["category_id"])
    for field in ("name", "description", "phone", "localidad", "category_id", "is_open_now"):
        if field in changes and changes[field] is None:
            changes.pop(field)  # campos obligatorios: no se pueden vaciar
    for field in ("tags", "amenities"):
        if field in changes and changes[field] is None:
            changes[field] = []
    for field, value in changes.items():
        setattr(business, field, value)
    db.commit()
    db.refresh(business)
    return business


def delete_business(db: Session, business: Business) -> None:
    db.query(Subscription).filter_by(business_id=business.id).delete()
    db.delete(business)
    db.commit()


def photos_limit(business: Business) -> int:
    subscription = business.subscription
    if subscription and subscription.status == SubscriptionStatus.active:
        return PLAN_FEATURES[subscription.plan]["photos_limit"]
    return FREE_PHOTOS_LIMIT


def recalculate_rating(db: Session, business_id: int) -> None:
    result = (
        db.query(func.avg(Review.rating).label("avg"), func.count(Review.id).label("count"))
        .filter(Review.business_id == business_id, Review.is_approved.is_(True))
        .first()
    )
    db.query(Business).filter(Business.id == business_id).update(
        {"rating_avg": round(float(result.avg or 0), 1), "rating_count": result.count or 0}
    )
    db.commit()


def record_event(db: Session, business_id: int, event_type: str) -> None:
    db.add(BusinessEvent(business_id=business_id, type=event_type, created_at=_utcnow()))
    db.commit()


def business_stats(db: Session, business_id: int, days: int = 30) -> dict:
    """Actividad reciente del perfil: es lo que el dueño mira para decidir si renueva."""
    since = _utcnow() - timedelta(days=days)

    def clicks(event_type: str) -> int:
        return (
            db.query(func.count(BusinessEvent.id))
            .filter(
                BusinessEvent.business_id == business_id,
                BusinessEvent.type == event_type,
                BusinessEvent.created_at >= since,
            )
            .scalar()
        )

    return {
        "days": days,
        "whatsapp_clicks": clicks("whatsapp"),
        "call_clicks": clicks("call"),
        "contacts": db.query(func.count(ContactRequest.id))
        .filter(ContactRequest.business_id == business_id, ContactRequest.created_at >= since)
        .scalar(),
        "reviews": db.query(func.count(Review.id))
        .filter(Review.business_id == business_id, Review.created_at >= since)
        .scalar(),
    }
