import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.business import LOCALIDADES_BOGOTA

DAYS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _clean_optional(v):
    """Convierte cadenas vacías en None (los formularios envían '')."""
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def _clean_phone(v: Optional[str], required: bool = False) -> Optional[str]:
    v = (v or "").strip()
    if not v:
        if required:
            raise ValueError("El teléfono es obligatorio")
        return None
    digits = re.sub(r"\D", "", v)
    if not 7 <= len(digits) <= 13:
        raise ValueError("El teléfono debe tener entre 7 y 13 dígitos")
    return v[:20]


def _clean_tags(v: Optional[List[str]]) -> Optional[List[str]]:
    if v is None:
        return None
    seen, out = set(), []
    for tag in v:
        tag = str(tag).strip()[:30]
        if tag and tag.lower() not in seen:
            seen.add(tag.lower())
            out.append(tag)
    return out[:10]


def _clean_schedule(v: Optional[dict]) -> Optional[dict]:
    if not v:
        return None
    out = {}
    for day in DAYS:
        entry = v.get(day)
        if not isinstance(entry, dict):
            continue
        closed = bool(entry.get("closed"))
        open_, close = entry.get("open") or "", entry.get("close") or ""
        if not closed and not (_TIME_RE.match(open_) and _TIME_RE.match(close)):
            raise ValueError(f"Horario inválido para {day}: usa el formato HH:MM")
        out[day] = {"open": open_, "close": close, "closed": closed}
    return out or None


def _clean_website(v: Optional[str]) -> Optional[str]:
    v = _clean_optional(v)
    if v and not re.match(r"^https?://", v, re.I):
        v = f"https://{v}"
    return v[:300] if v else None


def _clean_name(v: str) -> str:
    v = v.strip()
    if len(v) < 3:
        raise ValueError("El nombre debe tener al menos 3 caracteres")
    return v[:150]


def _clean_description(v: str) -> str:
    v = v.strip()
    if len(v) < 20:
        raise ValueError("La descripción debe tener al menos 20 caracteres")
    return v[:5000]


def _check_localidad(v: str) -> str:
    if v not in LOCALIDADES_BOGOTA:
        raise ValueError("Localidad no válida")
    return v


class _BusinessFields(BaseModel):
    @field_validator("short_description", "email", "address", "neighborhood", check_fields=False)
    @classmethod
    def empty_to_none(cls, v):
        return _clean_optional(v)

    @field_validator("website", check_fields=False)
    @classmethod
    def website_url(cls, v):
        return _clean_website(v)

    @field_validator("whatsapp", check_fields=False)
    @classmethod
    def whatsapp_valid(cls, v):
        return _clean_phone(v)

    @field_validator("tags", "amenities", check_fields=False)
    @classmethod
    def tags_clean(cls, v):
        return _clean_tags(v)

    @field_validator("schedule", check_fields=False)
    @classmethod
    def schedule_valid(cls, v):
        return _clean_schedule(v)


class BusinessCreate(_BusinessFields):
    name: str
    category_id: int
    description: str
    short_description: Optional[str] = None
    phone: str
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    localidad: str
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    tags: List[str] = []
    amenities: List[str] = []
    schedule: Optional[dict] = None

    @field_validator("name")
    @classmethod
    def name_min_length(cls, v):
        return _clean_name(v)

    @field_validator("description")
    @classmethod
    def description_min_length(cls, v):
        return _clean_description(v)

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, v):
        return _clean_phone(v, required=True)

    @field_validator("localidad")
    @classmethod
    def localidad_valid(cls, v):
        return _check_localidad(v)


class BusinessUpdate(_BusinessFields):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    localidad: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    tags: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    schedule: Optional[dict] = None
    is_open_now: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def name_min_length(cls, v):
        if v is None:
            return v
        return _clean_name(v)

    @field_validator("description")
    @classmethod
    def description_min_length(cls, v):
        if v is None:
            return v
        return _clean_description(v)

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, v):
        if v is None:
            return v
        return _clean_phone(v, required=True)

    @field_validator("localidad")
    @classmethod
    def localidad_valid(cls, v):
        if v is None:
            return v
        return _check_localidad(v)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    icon: str


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan: str
    status: str
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class BusinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str
    short_description: Optional[str]
    phone: str
    whatsapp: Optional[str]
    email: Optional[str]
    website: Optional[str]
    localidad: str
    address: Optional[str]
    neighborhood: Optional[str]
    logo_url: Optional[str]
    cover_url: Optional[str]
    photos: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    amenities: Optional[List[str]] = []
    rating_avg: float
    rating_count: int
    view_count: int
    contact_count: int
    status: str
    is_featured: bool
    is_open_now: bool
    schedule: Optional[dict]
    category: CategoryOut
    subscription: Optional[SubscriptionOut]
    created_at: datetime

    @field_validator("photos", "tags", "amenities", mode="before")
    @classmethod
    def none_to_list(cls, v):
        return v or []


class BusinessListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    short_description: Optional[str]
    phone: str
    localidad: str
    logo_url: Optional[str]
    tags: Optional[List[str]] = []
    rating_avg: float
    rating_count: int
    is_featured: bool
    is_open_now: bool
    schedule: Optional[dict] = None
    category: CategoryOut
    subscription: Optional[SubscriptionOut]

    @field_validator("tags", mode="before")
    @classmethod
    def none_to_list(cls, v):
        return v or []


class PaginatedBusinesses(BaseModel):
    items: List[BusinessListOut]
    total: int
    page: int
    pages: int
    per_page: int


class PhotoDelete(BaseModel):
    url: str


class AdminBusinessOut(BusinessOut):
    owner_id: int
    owner_email: Optional[str] = None
    owner_name: Optional[str] = None


class PaginatedAdminBusinesses(BaseModel):
    items: List[AdminBusinessOut]
    total: int
    page: int
    pages: int
    per_page: int
