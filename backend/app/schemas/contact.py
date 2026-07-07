from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactCreate(BaseModel):
    client_name: str
    client_phone: Optional[str] = None
    client_email: Optional[EmailStr] = None
    message: str
    service_requested: Optional[str] = None


class ContactOut(BaseModel):
    id: int
    client_name: str
    client_phone: Optional[str]
    client_email: Optional[str]
    message: str
    service_requested: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
