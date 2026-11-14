"""Ciclo de vida de las suscripciones: activación, renovación y vencimiento."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.business import Business, BusinessStatus
from app.models.subscription import PLAN_PRICES, PlanType, Subscription, SubscriptionStatus

SUBSCRIPTION_DAYS = 30


def _utcnow() -> datetime:
    # Se guarda en UTC sin tzinfo: MySQL DATETIME no conserva la zona horaria.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_naive(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is not None and dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def activate_subscription(
    db: Session,
    business_id: int,
    plan: PlanType,
    transaction_id: Optional[str] = None,
    days: int = SUBSCRIPTION_DAYS,
    amount_cop: Optional[float] = None,
) -> Optional[Subscription]:
    """
    Activa o renueva el plan de un negocio. Es idempotente por transacción:
    si la misma transacción de Wompi llega dos veces (webhook + verificación),
    solo se aplica una vez.
    """
    business = db.query(Business).filter_by(id=business_id).first()
    if not business:
        return None

    subscription = db.query(Subscription).filter_by(business_id=business_id).first()
    if subscription and transaction_id and subscription.wompi_transaction_id == transaction_id:
        return subscription

    now = _utcnow()
    if not subscription:
        subscription = Subscription(business_id=business_id)
        db.add(subscription)

    # Renovación anticipada del mismo plan: los días se suman al tiempo restante.
    current_end = _as_naive(subscription.expires_at)
    is_renewal = (
        subscription.status == SubscriptionStatus.active
        and subscription.plan == plan
        and current_end is not None
        and current_end > now
    )
    start_from = current_end if is_renewal else now
    if not is_renewal:
        subscription.started_at = now

    subscription.plan = plan
    subscription.status = SubscriptionStatus.active
    subscription.expires_at = start_from + timedelta(days=days)
    subscription.cancelled_at = None
    subscription.amount_cop = PLAN_PRICES[plan] if amount_cop is None else amount_cop
    if transaction_id:
        subscription.wompi_transaction_id = transaction_id

    if business.status in (BusinessStatus.pending, BusinessStatus.suspended):
        business.status = BusinessStatus.active
    business.is_featured = plan == PlanType.premium

    db.commit()
    db.refresh(subscription)
    return subscription


def expire_subscriptions(db: Session) -> int:
    """Marca como vencidas las suscripciones cuya fecha ya pasó. Devuelve cuántas."""
    expired = (
        db.query(Subscription)
        .filter(
            Subscription.status == SubscriptionStatus.active,
            Subscription.expires_at.isnot(None),
            Subscription.expires_at < _utcnow(),
        )
        .all()
    )
    for subscription in expired:
        subscription.status = SubscriptionStatus.expired
        business = db.query(Business).filter_by(id=subscription.business_id).first()
        if business:
            business.is_featured = False
    if expired:
        db.commit()
    return len(expired)


_last_sweep: Optional[datetime] = None


def expire_subscriptions_if_due(db: Session, every_minutes: int = 30) -> None:
    """Barrido perezoso: evita depender de un cron externo."""
    global _last_sweep
    now = _utcnow()
    if _last_sweep is None or now - _last_sweep > timedelta(minutes=every_minutes):
        _last_sweep = now
        expire_subscriptions(db)
