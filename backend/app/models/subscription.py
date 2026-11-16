from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class PlanType(str, enum.Enum):
    basic = "basic"
    premium = "premium"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    pending_payment = "pending_payment"


PLAN_PRICES = {
    PlanType.basic: 25000,      # COP
    PlanType.premium: 65000,    # COP
}

PLAN_FEATURES = {
    PlanType.basic: {
        "photos_limit": 3,
        "featured": False,
        "analytics": False,
        "schedule": True,
        "whatsapp_button": True,
        "agenda_online": False,
        "priority_support": False,
    },
    PlanType.premium: {
        "photos_limit": 10,
        "featured": True,
        "analytics": True,
        "schedule": True,
        "whatsapp_button": True,
        "agenda_online": True,
        "priority_support": True,
    },
}


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, unique=True)

    plan = Column(Enum(PlanType), nullable=False, default=PlanType.basic)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.pending_payment)

    # Wompi
    wompi_transaction_id = Column(String(200), nullable=True)
    wompi_subscription_id = Column(String(200), nullable=True)
    amount_cop = Column(Float, nullable=True)

    # Fechas
    started_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    # Cuándo se avisó al dueño que el plan está por vencer (se limpia al renovar)
    expiry_notified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    business = relationship("Business", back_populates="subscription")
