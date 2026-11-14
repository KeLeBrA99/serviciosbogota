from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from app.models.contact import ContactStatus


class ContactCreate(BaseModel):
    client_name: str
    client_phone: Optional[str] = None
    client_email: Optional[EmailStr] = None
    message: str
    service_requested: Optional[str] = None

    @field_validator("client_phone", "client_email", "service_requested", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    @field_validator("client_name")
    @classmethod
    def name_valid(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Escribe tu nombre")
        return v[:100]

    @field_validator("message")
    @classmethod
    def message_valid(cls, v):
        v = v.strip()
        if len(v) < 5:
            raise ValueError("El mensaje es demasiado corto")
        return v[:2000]

    @model_validator(mode="after")
    def needs_contact_way(self):
        if not self.client_phone and not self.client_email:
            raise ValueError("Deja un teléfono o un correo para que el negocio pueda responderte")
        if self.client_phone:
            self.client_phone = self.client_phone[:20]
        return self


class ContactStatusUpdate(BaseModel):
    status: ContactStatus


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_name: str
    client_phone: Optional[str]
    client_email: Optional[str]
    message: str
    service_requested: Optional[str]
    status: str
    created_at: datetime
