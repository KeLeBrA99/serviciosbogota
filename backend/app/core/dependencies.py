from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.database import get_db
from app.models.business import Business
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)


def _user_from_token(token: str, db: Session) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    return _user_from_token(credentials.credentials, db)


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a este recurso",
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        return _user_from_token(credentials.credentials, db)
    except HTTPException:
        return None


def get_owned_business(db: Session, business_id: int, user: User) -> Business:
    """Devuelve el negocio si pertenece al usuario (o si el usuario es admin)."""
    query = db.query(Business).filter(Business.id == business_id)
    if user.role != UserRole.admin:
        query = query.filter(Business.owner_id == user.id)
    business = query.first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return business
