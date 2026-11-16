from typing import Optional

from pydantic import BaseModel, Field

from app.models.subscription import PlanType


class CheckoutRequest(BaseModel):
    business_id: int
    plan: PlanType


class CheckoutResponse(BaseModel):
    public_key: str
    currency: str
    amount_in_cents: int
    reference: str
    redirect_url: str
    checkout_url: str


class PaymentVerification(BaseModel):
    transaction_id: str
    status: str  # APPROVED, DECLINED, PENDING, VOIDED, ERROR
    business_id: Optional[int] = None
    plan: Optional[str] = None
    activated: bool = False


class ManualSubscription(BaseModel):
    """Activación manual por el admin (p. ej. pago por transferencia o Nequi)."""
    plan: PlanType
    days: int = Field(30, ge=1, le=366)
