from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subscription import PlanType
from app.services.wompi_service import create_payment_link, handle_wompi_webhook

router = APIRouter(prefix="/payments", tags=["Pagos"])


@router.post("/checkout")
def checkout(
    business_id: int,
    plan: PlanType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Genera el enlace de pago de Wompi para activar un plan."""
    return create_payment_link(business_id, plan, current_user.email)


@router.post("/wompi-webhook")
async def wompi_webhook(request: Request, db: Session = Depends(get_db)):
    """Recibe notificaciones de pago de Wompi."""
    signature = request.headers.get("x-event-checksum", "")
    event = await request.json()
    return handle_wompi_webhook(db, event, signature)
