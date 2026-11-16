from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_optional_user, get_owned_business
from app.core.limiter import limiter
from app.db.database import get_db
from app.models.business import Business, BusinessStatus
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut, ReviewResponse
from app.services.business_service import recalculate_rating
from app.services.email_service import send_new_review_email

router = APIRouter(prefix="/businesses/{business_id}/reviews", tags=["Reseñas"])


@router.get("", response_model=list[ReviewOut])
def list_reviews(business_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Review)
        .filter(Review.business_id == business_id, Review.is_approved.is_(True))
        .order_by(Review.created_at.desc(), Review.id.desc())
        .limit(200)
        .all()
    )


@router.post("", response_model=ReviewOut, status_code=201)
@limiter.limit("5/hour")
def create_review(
    request: Request,
    business_id: int,
    data: ReviewCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    business = (
        db.query(Business)
        .filter(Business.id == business_id, Business.status == BusinessStatus.active)
        .first()
    )
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    if user:
        if user.id == business.owner_id:
            raise HTTPException(status_code=403, detail="No puedes reseñar tu propio negocio")
        if db.query(Review).filter_by(business_id=business_id, author_id=user.id).first():
            raise HTTPException(status_code=409, detail="Ya dejaste una reseña para este negocio")

    review = Review(business_id=business_id, author_id=user.id if user else None, **data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    recalculate_rating(db, business_id)

    owner = db.query(User).filter(User.id == business.owner_id).first()
    if owner:
        background.add_task(
            send_new_review_email,
            owner_email=owner.email,
            business_name=business.name,
            business_slug=business.slug,
            author_name=review.author_name,
            rating=review.rating,
            comment=review.comment,
        )
    return review


@router.put("/{review_id}/response", response_model=ReviewOut)
def respond_review(
    business_id: int,
    review_id: int,
    data: ReviewResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """El dueño del negocio responde públicamente a una reseña."""
    get_owned_business(db, business_id, current_user)
    review = db.query(Review).filter_by(id=review_id, business_id=business_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    review.response = data.response
    db.commit()
    db.refresh(review)
    return review
