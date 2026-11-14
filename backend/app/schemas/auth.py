from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


def _validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if len(v.encode()) > 72:
        raise ValueError("La contraseña es demasiado larga (máximo 72 caracteres)")
    return v


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

    @field_validator("email")
    @classmethod
    def email_lower(cls, v):
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        return _validate_password(v)

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()[:150]

    @field_validator("phone")
    @classmethod
    def phone_clean(cls, v):
        v = (v or "").strip()
        return v[:20] or None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def email_lower(cls, v):
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        return _validate_password(v)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
