import hashlib
import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings
from app.models.subscription import Subscription, PlanType, SubscriptionStatus, PLAN_PRICES
from app.models.business import Business, BusinessStatus


def generate_wompi_signature(properties: list, secret: str) -> str:
    """Genera firma para verificar eventos de Wompi."""
    concatenated = "".join(str(p) for p in properties) + secret
    return hashlib.sha256(concatenated.encode()).hexdigest()


def create_payment_link(business_id: int, plan: PlanType, user_email: str) -> dict:
    """Crea un enlace de pago en Wompi para activar un plan."""
    amount_cents = PLAN_PRICES[plan] * 100  # Wompi recibe centavos
    reference = f"svc-{business_id}-{plan}-{int(datetime.now().timestamp())}"

    return {
        "public_key": settings.WOMPI_PUBLIC_KEY,
        "currency": "COP",
        "amount_in_cents": amount_cents,
        "reference": reference,
        "customer_email": user_email,
        "redirect_url": f"{settings.FRONTEND_URL}/pago/confirmacion",
        "checkout_url": f"https://checkout.wompi.co/p/?public-key={settings.WOMPI_PUBLIC_KEY}&currency=COP&amount-in-cents={amount_cents}&reference={reference}",
    }


def handle_wompi_webhook(db: Session, event: dict, signature_header: str) -> dict:
    """
    Maneja el webhook de Wompi cuando se completa un pago.
    Activa o cancela el plan del negocio.
    """
    # Verificar firma
    data = event.get("data", {})
    checksum = event.get("signature", {}).get("checksum", "")
    properties = event.get("signature", {}).get("properties", [])
    prop_values = [data.get(p) for p in properties]
    expected = generate_wompi_signature(prop_values, settings.WOMPI_EVENTS_SECRET)

    if checksum != expected:
        raise HTTPException(status_code=400, detail="Firma de Wompi inválida")

    event_type = event.get("event")
    transaction = data.get("transaction", {})
    reference = transaction.get("reference", "")
    wompi_id = transaction.get("id", "")
    tx_status = transaction.get("status", "")

    # Parsear referencia: svc-{business_id}-{plan}-{timestamp}
    parts = reference.split("-")
    if len(parts) < 3 or parts[0] != "svc":
        return {"status": "ignored"}

    business_id = int(parts[1])
    plan_str = parts[2]

    if tx_status == "APPROVED":
        _activate_subscription(db, business_id, plan_str, wompi_id)

    return {"status": "processed"}


def _activate_subscription(db: Session, business_id: int, plan_str: str, wompi_id: str):
    plan = PlanType(plan_str)
    subscription = db.query(Subscription).filter_by(business_id=business_id).first()
    if not subscription:
        subscription = Subscription(business_id=business_id)
        db.add(subscription)

    subscription.plan = plan
    subscription.status = SubscriptionStatus.active
    subscription.wompi_transaction_id = wompi_id
    subscription.started_at = datetime.now(timezone.utc)
    subscription.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    subscription.amount_cop = PLAN_PRICES[plan]

    # Activar negocio
    business = db.query(Business).filter_by(id=business_id).first()
    if business:
        business.status = BusinessStatus.active
        if plan == PlanType.premium:
            business.is_featured = True

    db.commit()
