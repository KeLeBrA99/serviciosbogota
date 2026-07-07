from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Puede ser anónimo

    # Contenido
    author_name = Column(String(100), nullable=False)   # Nombre visible
    rating = Column(Float, nullable=False)               # 1.0 - 5.0
    comment = Column(Text, nullable=True)
    response = Column(Text, nullable=True)               # Respuesta del negocio

    # Moderación
    is_approved = Column(Boolean, default=True)
    is_flagged = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="reviews")
    author = relationship("User", back_populates="reviews")
