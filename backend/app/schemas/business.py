from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List, Any
from datetime import datetime
from app.models.business import BusinessStatus


class BusinessCreate(BaseModel):
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
    schedule: Optional[dict] = None

    @field_validator("name")
    @classmethod
    def name_min_length(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        return v.strip()


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
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
    schedule: Optional[dict] = None
    is_open_now: Optional[bool] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: str

    class Config:
        from_attributes = True


class SubscriptionOut(BaseModel):
    plan: str
    status: str
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessOut(BaseModel):
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
    photos: List[str]
    tags: List[str]
    amenities: List[str]
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

    class Config:
        from_attributes = True


class BusinessListOut(BaseModel):
    id: int
    name: str
    slug: str
    short_description: Optional[str]
    phone: str
    localidad: str
    logo_url: Optional[str]
    tags: List[str]
    rating_avg: float
    rating_count: int
    is_featured: bool
    is_open_now: bool
    category: CategoryOut
    subscription: Optional[SubscriptionOut]

    class Config:
        from_attributes = True


class PaginatedBusinesses(BaseModel):
    items: List[BusinessListOut]
    total: int
    page: int
    pages: int
    per_page: int
