from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    author_name: str
    rating: float
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if not (1.0 <= v <= 5.0):
            raise ValueError("La calificación debe estar entre 1 y 5")
        return round(v * 2) / 2  # Redondea a 0.5


class ReviewResponse(BaseModel):
    response: str


class ReviewOut(BaseModel):
    id: int
    author_name: str
    rating: float
    comment: Optional[str]
    response: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
