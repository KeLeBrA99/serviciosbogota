from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String

from app.db.database import Base

EVENT_TYPES = ("whatsapp", "call")


class BusinessEvent(Base):
    """
    Interacción de un visitante con un perfil (clic en WhatsApp o en llamar).
    Se guarda una fila por clic para poder mostrar cifras por periodo.
    """
    __tablename__ = "business_events"
    __table_args__ = (Index("ix_business_events_business_created", "business_id", "created_at"),)

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
