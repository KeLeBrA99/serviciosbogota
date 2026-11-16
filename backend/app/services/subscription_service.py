"""Ciclo de vida de las suscripciones: activación, renovación y vencimiento."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.business import Business, BusinessStatus
from app.models.subscription import PLAN_PRICES, PlanType, Subscription, SubscriptionStatus
from app.models.user import User
from app.services import email_service

SUBSCRIPTION_DAYS = 30
REMINDER_DAYS = 5  # con cuántos días de anticipación se avisa el vencimiento
PLAN_NAMES = {PlanType.basic: "Básico", PlanType.premium: "Premium"}
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
BOGOTA_OFFSET = timedelta(hours=-5)  # Colombia no tiene horario de verano


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
    subscription.expiry_notified_at = None  # un plan renovado vuelve a recibir su recordatorio
    subscription.amount_cop = PLAN_PRICES[plan] if amount_cop is None else amount_cop
    if transaction_id:
        subscription.wompi_transaction_id = transaction_id

    if business.status in (BusinessStatus.pending, BusinessStatus.suspended):
        business.status = BusinessStatus.active
    business.is_featured = plan == PlanType.premium

    db.commit()
    db.refresh(subscription)
    return subscription


def _owner_email(db: Session, business: Business) -> Optional[str]:
    owner = db.query(User).filter(User.id == business.owner_id).first()
    return owner.email if owner and owner.is_active else None


def _format_date(dt: datetime) -> str:
    local = dt + BOGOTA_OFFSET
    return f"{local.day} de {MONTHS[local.month - 1]} de {local.year}"


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
    notices = []
    for subscription in expired:
        subscription.status = SubscriptionStatus.expired
        business = db.query(Business).filter_by(id=subscription.business_id).first()
        if business:
            business.is_featured = False
            email = _owner_email(db, business)
            if email:
                notices.append((email, business.name, business.id, PLAN_NAMES[subscription.plan]))
    if expired:
        db.commit()
    for notice in notices:  # los correos salen después de guardar el cambio
        email_service.send_plan_expired_email(*notice)
    return len(expired)


def send_expiry_reminders(db: Session) -> int:
    """
    Avisa una sola vez a los dueños cuyo plan vence en los próximos REMINDER_DAYS
    días. Devuelve cuántos recordatorios quedaron registrados.
    """
    now = _utcnow()
    due = (
        db.query(Subscription)
        .filter(
            Subscription.status == SubscriptionStatus.active,
            Subscription.expires_at.isnot(None),
            Subscription.expires_at >= now,
            Subscription.expires_at <= now + timedelta(days=REMINDER_DAYS),
            Subscription.expiry_notified_at.is_(None),
        )
        .all()
    )
    count = 0
    for subscription in due:
        business = db.query(Business).filter_by(id=subscription.business_id).first()
        email = _owner_email(db, business) if business else None
        if not email:
            continue
        expires_at = _as_naive(subscription.expires_at)
        days_left = max(0, (expires_at - now).days)
        sent = email_service.send_plan_expiring_email(
            email, business.name, business.id, PLAN_NAMES[subscription.plan], _format_date(expires_at), days_left
        )
        # Si el proveedor falló se reintenta en el siguiente barrido; sin proveedor
        # configurado se marca igual, para no repetir el aviso en el log cada hora.
        if sent or not settings.email_enabled:
            subscription.expiry_notified_at = now
            db.commit()
            count += 1
    return count


def run_subscription_sweep(db: Session) -> dict:
    """Tarea periódica: vence planes y envía recordatorios."""
    return {"expired": expire_subscriptions(db), "reminders": send_expiry_reminders(db)}


_last_sweep: Optional[datetime] = None


def expire_subscriptions_if_due(db: Session, every_minutes: int = 30) -> None:
    """Barrido perezoso al listar negocios; complementa la tarea periódica."""
    global _last_sweep
    now = _utcnow()
    if _last_sweep is None or now - _last_sweep > timedelta(minutes=every_minutes):
        _last_sweep = now
        expire_subscriptions(db)
