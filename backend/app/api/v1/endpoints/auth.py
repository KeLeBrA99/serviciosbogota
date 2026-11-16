from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)
from app.services.auth_service import (
    change_password,
    login_user,
    refresh_tokens,
    register_user,
    reset_password,
    start_password_reset,
    tokens_for_user,
)
from app.services.email_service import send_password_reset_email

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


@router.post("/forgot-password")
@limiter.limit("5/hour")
def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Envía el enlace para restablecer la contraseña. La respuesta es siempre la
    misma, exista o no la cuenta, para no revelar qué correos están registrados.
    """
    result = start_password_reset(db, data.email)
    if result:
        user, token = result
        background.add_task(send_password_reset_email, user.email, user.full_name, token)
    return {"message": "Si el correo está registrado, te enviamos un enlace para restablecer la contraseña."}


@router.post("/reset-password", status_code=204)
@limiter.limit("10/hour")
def reset_password_endpoint(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_password(db, data.token, data.new_password)
