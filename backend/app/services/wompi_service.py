"""
Integración con Wompi (Web Checkout).

Flujo:
1. `create_checkout` arma el enlace de pago firmado (firma de integridad).
2. El usuario paga en Wompi y vuelve a /pago/confirmacion?id=<transacción>.
3. El plan se activa por dos vías, ambas idempotentes:
   - el webhook de eventos (`handle_wompi_webhook`), y
   - la verificación directa contra la API de Wompi (`verify_transaction`).
"""
import hashlib
import hmac
import time
from typing import Any, Optional, Tuple
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.subscription import PLAN_PRICES, PlanType
from app.services.subscription_service import activate_subscription

CHECKOUT_URL = "https://checkout.wompi.co/p/"
CURRENCY = "COP"


def integrity_signature(reference: str, amount_in_cents: int, currency: str, secret: str) -> str:
    """Firma de integridad: SHA256(referencia + monto en centavos + moneda + secreto)."""
    return hashlib.sha256(f"{reference}{amount_in_cents}{currency}{secret}".encode()).hexdigest()


def build_reference(business_id: int, plan: PlanType) -> str:
    return f"svc-{business_id}-{plan.value}-{int(time.time())}"


def parse_reference(reference: str) -> Optional[Tuple[int, PlanType]]:
    """Referencia: svc-{business_id}-{plan}-{timestamp}."""
    parts = (reference or "").split("-")
    if len(parts) != 4 or parts[0] != "svc":
        return None
    try:
        return int(parts[1]), PlanType(parts[2])
    except ValueError:
        return None


def create_checkout(business_id: int, plan: PlanType, user_email: str) -> dict:
    if not settings.wompi_enabled:
        raise HTTPException(
            status_code=503,
            detail="Los pagos en línea aún no están habilitados. Escríbenos para activar tu plan.",
        )
    amount_cents = PLAN_PRICES[plan] * 100  # Wompi recibe centavos
    reference = build_reference(business_id, plan)
    redirect_url = f"{settings.FRONTEND_URL.rstrip('/')}/pago/confirmacion"

    params = {
        "public-key": settings.WOMPI_PUBLIC_KEY,
        "currency": CURRENCY,
        "amount-in-cents": amount_cents,
        "reference": reference,
        "redirect-url": redirect_url,
        "customer-data:email": user_email,
    }
    if settings.WOMPI_INTEGRITY_SECRET:
        params["signature:integrity"] = integrity_signature(
            reference, amount_cents, CURRENCY, settings.WOMPI_INTEGRITY_SECRET
        )

    return {
        "public_key": settings.WOMPI_PUBLIC_KEY,
        "currency": CURRENCY,
        "amount_in_cents": amount_cents,
        "reference": reference,
        "redirect_url": redirect_url,
        "checkout_url": f"{CHECKOUT_URL}?{urlencode(params)}",
    }


def _resolve(data: dict, path: str) -> Any:
    """Resuelve rutas tipo 'transaction.amount_in_cents' dentro de event.data."""
    value: Any = data
    for key in path.split("."):
        if not isinstance(value, dict):
            return ""
        value = value.get(key, "")
    return value


def event_checksum(event: dict, secret: str) -> str:
    """
    Checksum de eventos de Wompi:
    SHA256(valores de signature.properties + timestamp + secreto de eventos).
    """
    data = event.get("data", {})
    properties = event.get("signature", {}).get("properties", [])
    concatenated = "".join(str(_resolve(data, p)) for p in properties)
    concatenated += f"{event.get('timestamp', '')}{secret}"
    return hashlib.sha256(concatenated.encode()).hexdigest()


def _apply_transaction(db: Session, transaction: dict) -> Tuple[Optional[int], Optional[PlanType], bool]:
    """Activa el plan si la transacción está aprobada y el monto corresponde."""
    parsed = parse_reference(transaction.get("reference", ""))
    if not parsed:
        return None, None, False
    business_id, plan = parsed

    if transaction.get("status") != "APPROVED":
        return business_id, plan, False
    if (
        transaction.get("amount_in_cents") != PLAN_PRICES[plan] * 100
        or transaction.get("currency", CURRENCY) != CURRENCY
    ):
        # Monto alterado: no se activa nada.
        return business_id, plan, False

    subscription = activate_subscription(db, business_id, plan, transaction_id=str(transaction.get("id", "")))
    return business_id, plan, subscription is not None


def handle_wompi_webhook(db: Session, event: dict, header_checksum: str = "") -> dict:
    """Webhook de eventos de Wompi (configurar la URL en el panel de Wompi)."""
    if not settings.WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=503, detail="Webhook de Wompi no configurado")

    expected = event_checksum(event, settings.WOMPI_EVENTS_SECRET)
    received = (event.get("signature", {}).get("checksum") or header_checksum or "").lower()
    if not hmac.compare_digest(expected, received):
        raise HTTPException(status_code=400, detail="Firma de Wompi inválida")

    if event.get("event") != "transaction.updated":
        return {"status": "ignored"}

    transaction = event.get("data", {}).get("transaction", {})
    business_id, _, activated = _apply_transaction(db, transaction)
    if business_id is None:
        return {"status": "ignored"}
    return {"status": "processed", "activated": activated}


def fetch_transaction(transaction_id: str) -> dict:
    """Consulta una transacción en la API de Wompi (endpoint público)."""
    url = f"{settings.WOMPI_BASE_URL.rstrip('/')}/transactions/{transaction_id}"
    try:
        response = httpx.get(url, timeout=10)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="No se pudo consultar el pago en Wompi")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="No se pudo consultar el pago en Wompi")
    return response.json().get("data", {})


def verify_transaction(db: Session, transaction_id: str) -> dict:
    """Verifica el pago directamente con Wompi; no depende del webhook."""
    transaction = fetch_transaction(transaction_id)
    business_id, plan, activated = _apply_transaction(db, transaction)
    return {
        "transaction_id": transaction_id,
        "status": transaction.get("status", "ERROR"),
        "business_id": business_id,
        "plan": plan.value if plan else None,
        "activated": activated,
    }
