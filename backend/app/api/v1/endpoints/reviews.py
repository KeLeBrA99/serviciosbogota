from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.review import ReviewCreate, ReviewOut
from app.models.review import Review
from app.models.business import Business
from app.services.business_service import recalculate_rating
from fastapi import HTTPException

router = APIRouter(prefix="/businesses/{business_id}/reviews", tags=["Reseñas"])


@router.get("/", response_model=list[ReviewOut])
def list_reviews(business_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Review)
        .filter(Review.business_id == business_id, Review.is_approved == True)
        .order_by(Review.created_at.desc())
        .all()
    )


@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(business_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    if not db.query(Business).filter_by(id=business_id).first():
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    review = Review(business_id=business_id, **data.model_dump())
    db.add(review)
    db.commit()
    recalculate_rating(db, business_id)
    db.refresh(review)
    return review
