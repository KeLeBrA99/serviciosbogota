from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.contact import ContactRequest, ContactStatus
from app.models.business import Business
from app.schemas.contact import ContactCreate, ContactOut

router = APIRouter(tags=["Contactos"])


@router.post("/businesses/{business_id}/contact", response_model=ContactOut, status_code=201)
def send_contact(business_id: int, data: ContactCreate, db: Session = Depends(get_db)):
    business = db.query(Business).filter_by(id=business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    contact = ContactRequest(business_id=business_id, **data.model_dump())
    db.add(contact)
    business.contact_count += 1
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/my-businesses/{business_id}/contacts", response_model=list[ContactOut])
def get_contacts(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == current_user.id,
    ).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return (
        db.query(ContactRequest)
        .filter_by(business_id=business_id)
        .order_by(ContactRequest.created_at.desc())
        .all()
    )
