from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.auth_service import (
    change_password,
    login_user,
    refresh_tokens,
    register_user,
    tokens_for_user,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("10/hour")
def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data)
    return tokens_for_user(user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, data)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return refresh_tokens(db, data.refresh_token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password", status_code=204)
def update_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_password(db, current_user, data)
