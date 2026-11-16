from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_admin
from app.db.database import get_db
from app.models.business import Business, BusinessStatus
from app.models.contact import ContactRequest
from app.models.review import Review
from app.models.subscription import PlanType, Subscription, SubscriptionStatus
from app.models.user import User
from app.schemas.auth import UserOut
from app.schemas.business import AdminBusinessOut, PaginatedAdminBusinesses
from app.schemas.payment import ManualSubscription
from app.schemas.review import AdminReviewOut
from app.services.business_service import recalculate_rating
from app.services.subscription_service import (
    activate_subscription,
    expire_subscriptions,
    run_subscription_sweep,
)

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


def _get_business(db: Session, business_id: int) -> Business:
    business = db.query(Business).filter_by(id=business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return business


def _set_status(db: Session, business_id: int, status: BusinessStatus, message: str) -> dict:
    business = _get_business(db, business_id)
    business.status = status
    if status != BusinessStatus.active:
        business.is_featured = False
    db.commit()
    return {"message": message, "status": status.value}


@router.get("/stats")
def global_stats(db: Session = Depends(get_db)):
    expire_subscriptions(db)
    active_subs = db.query(Subscription).filter_by(status=SubscriptionStatus.active)
    return {
        "total_businesses": db.query(Business).count(),
        "active_businesses": db.query(Business).filter_by(status=BusinessStatus.active).count(),
        "pending_businesses": db.query(Business).filter_by(status=BusinessStatus.pending).count(),
        "suspended_businesses": db.query(Business).filter_by(status=BusinessStatus.suspended).count(),
        "active_subscriptions": active_subs.count(),
        "premium_subscriptions": active_subs.filter(Subscription.plan == PlanType.premium).count(),
        "monthly_revenue_cop": sum(s.amount_cop or 0 for s in active_subs.all()),
        "total_users": db.query(User).count(),
        "total_reviews": db.query(Review).count(),
        "total_contacts": db.query(ContactRequest).count(),
    }


@router.get("/businesses", response_model=PaginatedAdminBusinesses)
def list_businesses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[BusinessStatus] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    db: Session = Depends(get_db),
):
    query = db.query(Business).options(
        joinedload(Business.category), joinedload(Business.subscription), joinedload(Business.owner)
    )
    if status:
        query = query.filter(Business.status == status)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(Business.name.ilike(term), Business.phone.ilike(term)))
    total = query.count()
    rows = (
        query.order_by(Business.created_at.desc(), Business.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    items = []
    for b in rows:
        item = AdminBusinessOut.model_validate(b)
        item.owner_email = b.owner.email if b.owner else None
        item.owner_name = b.owner.full_name if b.owner else None
        items.append(item)
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": max(1, -(-total // per_page)),
        "per_page": per_page,
    }


@router.patch("/businesses/{business_id}/approve")
def approve_business(business_id: int, db: Session = Depends(get_db)):
    return _set_status(db, business_id, BusinessStatus.active, "Negocio aprobado")


@router.patch("/businesses/{business_id}/suspend")
def suspend_business(business_id: int, db: Session = Depends(get_db)):
    return _set_status(db, business_id, BusinessStatus.suspended, "Negocio suspendido")


@router.patch("/businesses/{business_id}/reject")
def reject_business(business_id: int, db: Session = Depends(get_db)):
    return _set_status(db, business_id, BusinessStatus.rejected, "Negocio rechazado")


@router.patch("/businesses/{business_id}/featured")
def toggle_featured(business_id: int, featured: bool = Query(...), db: Session = Depends(get_db)):
    business = _get_business(db, business_id)
    business.is_featured = featured
    db.commit()
    return {"message": "Destacado actualizado", "is_featured": featured}


@router.post("/businesses/{business_id}/subscription")
def manual_subscription(business_id: int, data: ManualSubscription, db: Session = Depends(get_db)):
    """Activa un plan a mano (pago por transferencia, Nequi, cortesía, etc.)."""
    _get_business(db, business_id)
    subscription = activate_subscription(db, business_id, data.plan, days=data.days)
    return {
        "message": "Plan activado",
        "plan": subscription.plan.value,
        "expires_at": subscription.expires_at,
    }


@router.post("/subscriptions/expire")
def run_expiration(db: Session = Depends(get_db)):
    """Vence planes y envía recordatorios ahora mismo (también corre solo cada hora)."""
    return run_subscription_sweep(db)


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc(), User.id.desc()).limit(500).all()


@router.get("/reviews", response_model=list[AdminReviewOut])
def list_reviews(db: Session = Depends(get_db)):
    rows = (
        db.query(Review)
        .options(joinedload(Review.business))
        .order_by(Review.created_at.desc(), Review.id.desc())
        .limit(200)
        .all()
    )
    out = []
    for r in rows:
        item = AdminReviewOut.model_validate(r)
        item.business_name = r.business.name if r.business else None
        out.append(item)
    return out


@router.patch("/reviews/{review_id}/visibility")
def set_review_visibility(review_id: int, visible: bool = Query(...), db: Session = Depends(get_db)):
    review = db.query(Review).filter_by(id=review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    review.is_approved = visible
    db.commit()
    recalculate_rating(db, review.business_id)
    return {"message": "Reseña actualizada", "is_approved": visible}
