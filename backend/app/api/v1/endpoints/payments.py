from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_owned_business
from app.db.database import get_db
from app.models.subscription import PLAN_FEATURES, PLAN_PRICES, PlanType
from app.models.user import User
from app.schemas.payment import CheckoutRequest, CheckoutResponse, PaymentVerification
from app.services.wompi_service import create_checkout, handle_wompi_webhook, verify_transaction

router = APIRouter(prefix="/payments", tags=["Pagos"])


@router.get("/plans")
def plans():
    """Planes disponibles con su precio mensual en COP."""
    return [
        {"plan": plan.value, "price_cop": PLAN_PRICES[plan], "features": PLAN_FEATURES[plan]}
        for plan in PlanType
    ]


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Genera el enlace de pago de Wompi para activar o renovar un plan."""
    business = get_owned_business(db, data.business_id, current_user)
    return create_checkout(business.id, data.plan, current_user.email)


@router.get("/verify/{transaction_id}", response_model=PaymentVerification)
def verify(transaction_id: str, db: Session = Depends(get_db)):
    """
    Confirma un pago consultando a Wompi. Lo usa la página de confirmación;
    el resultado depende solo de lo que responda Wompi, no del navegador.
    """
    return verify_transaction(db, transaction_id)


@router.post("/wompi-webhook")
async def wompi_webhook(request: Request, db: Session = Depends(get_db)):
    """Recibe los eventos de pago de Wompi."""
    event = await request.json()
    return handle_wompi_webhook(db, event, request.headers.get("x-event-checksum", ""))
