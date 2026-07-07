from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.business import Business, BusinessStatus
from app.models.subscription import Subscription, SubscriptionStatus

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def global_stats(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    return {
        "total_businesses": db.query(Business).count(),
        "active_businesses": db.query(Business).filter_by(status=BusinessStatus.active).count(),
        "pending_businesses": db.query(Business).filter_by(status=BusinessStatus.pending).count(),
        "active_subscriptions": db.query(Subscription).filter_by(status=SubscriptionStatus.active).count(),
        "total_users": db.query(User).count(),
    }


@router.patch("/businesses/{business_id}/approve")
def approve_business(
    business_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    business = db.query(Business).filter_by(id=business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    business.status = BusinessStatus.active
    db.commit()
    return {"message": "Negocio aprobado"}


@router.patch("/businesses/{business_id}/suspend")
def suspend_business(
    business_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    business = db.query(Business).filter_by(id=business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    business.status = BusinessStatus.suspended
    db.commit()
    return {"message": "Negocio suspendido"}
