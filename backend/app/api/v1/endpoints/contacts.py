from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_owned_business
from app.core.limiter import limiter
from app.db.database import get_db
from app.models.business import Business, BusinessStatus
from app.models.contact import ContactRequest
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactOut, ContactStatusUpdate
from app.services.email_service import send_new_contact_email

router = APIRouter(tags=["Contactos"])


@router.post("/businesses/{business_id}/contact", response_model=ContactOut, status_code=201)
@limiter.limit("10/hour")
def send_contact(
    request: Request,
    business_id: int,
    data: ContactCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    business = (
        db.query(Business)
        .filter(Business.id == business_id, Business.status == BusinessStatus.active)
        .first()
    )
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    contact = ContactRequest(business_id=business_id, **data.model_dump())
    db.add(contact)
    business.contact_count = (business.contact_count or 0) + 1
    db.commit()
    db.refresh(contact)

    # El correo sale después de responder, para no hacer esperar al cliente.
    owner = db.query(User).filter(User.id == business.owner_id).first()
    if owner:
        background.add_task(
            send_new_contact_email,
            owner_email=owner.email,
            business_name=business.name,
            client_name=contact.client_name,
            message=contact.message,
            client_phone=contact.client_phone,
            client_email=contact.client_email,
        )
    return contact


@router.get("/my-businesses/{business_id}/contacts", response_model=list[ContactOut])
def get_contacts(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_business(db, business_id, current_user)
    return (
        db.query(ContactRequest)
        .filter_by(business_id=business_id)
        .order_by(ContactRequest.created_at.desc(), ContactRequest.id.desc())
        .limit(200)
        .all()
    )


@router.patch("/my-businesses/{business_id}/contacts/{contact_id}", response_model=ContactOut)
def update_contact_status(
    business_id: int,
    contact_id: int,
    data: ContactStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_business(db, business_id, current_user)
    contact = db.query(ContactRequest).filter_by(id=contact_id, business_id=business_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    contact.status = data.status
    db.commit()
    db.refresh(contact)
    return contact
