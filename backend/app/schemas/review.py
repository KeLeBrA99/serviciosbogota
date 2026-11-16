from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ReviewCreate(BaseModel):
    author_name: str
    rating: float
    comment: Optional[str] = None

    @field_validator("author_name")
    @classmethod
    def name_valid(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Escribe tu nombre")
        return v[:100]

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if not (1.0 <= v <= 5.0):
            raise ValueError("La calificación debe estar entre 1 y 5")
        return round(v * 2) / 2  # Redondea a 0.5

    @field_validator("comment")
    @classmethod
    def comment_clean(cls, v):
        v = (v or "").strip()
        return v[:2000] or None


class ReviewResponse(BaseModel):
    response: str

    @field_validator("response")
    @classmethod
    def response_valid(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("La respuesta no puede estar vacía")
        return v[:2000]


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str
    rating: float
    comment: Optional[str]
    response: Optional[str]
    created_at: datetime


class AdminReviewOut(ReviewOut):
    business_id: int
    is_approved: bool
    business_name: Optional[str] = None
