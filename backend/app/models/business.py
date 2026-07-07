from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, Float, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class BusinessStatus(str, enum.Enum):
    pending = "pending"       # Recién registrado, esperando activación
    active = "active"         # Activo y visible
    suspended = "suspended"   # Suspendido por pago vencido
    rejected = "rejected"     # Rechazado por admin


LOCALIDADES_BOGOTA = [
    "Usaquén", "Chapinero", "Santa Fe", "San Cristóbal", "Usme",
    "Tunjuelito", "Bosa", "Kennedy", "Fontibón", "Engativá",
    "Suba", "Barrios Unidos", "Teusaquillo", "Los Mártires",
    "Antonio Nariño", "Puente Aranda", "La Candelaria",
    "Rafael Uribe Uribe", "Ciudad Bolívar", "Sumapaz"
]


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Info básica
    name = Column(String(150), nullable=False, index=True)
    slug = Column(String(200), unique=True, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(String(300), nullable=True)

    # Contacto
    phone = Column(String(20), nullable=False)
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(300), nullable=True)

    # Ubicación
    localidad = Column(String(100), nullable=False, index=True)
    address = Column(String(300), nullable=True)
    neighborhood = Column(String(150), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Media
    logo_url = Column(String(500), nullable=True)
    cover_url = Column(String(500), nullable=True)
    photos = Column(JSON, default=list)   # Lista de URLs

    # Etiquetas y atributos
    tags = Column(JSON, default=list)           # ["Domicilio", "24h", ...]
    amenities = Column(JSON, default=list)      # ["Parqueadero", "WiFi", ...]
    service_areas = Column(JSON, default=list)  # Otras localidades que cubre

    # Horarios
    schedule = Column(JSON, nullable=True)
    # { "lunes": {"open": "08:00", "close": "18:00", "closed": false}, ... }

    # Métricas
    rating_avg = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    contact_count = Column(Integer, default=0)

    # Estado
    status = Column(Enum(BusinessStatus), default=BusinessStatus.pending)
    is_featured = Column(Boolean, default=False)   # Destacado en home
    is_open_now = Column(Boolean, default=True)    # Override manual

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    owner = relationship("User", back_populates="businesses")
    category = relationship("Category", back_populates="businesses")
    reviews = relationship("Review", back_populates="business", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="business", uselist=False)
    contacts = relationship("ContactRequest", back_populates="business", cascade="all, delete-orphan")
