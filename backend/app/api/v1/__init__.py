from fastapi import APIRouter
from app.api.v1.endpoints import auth, businesses, categories, reviews, contacts, payments, admin

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(businesses.router)
router.include_router(categories.router)
router.include_router(reviews.router)
router.include_router(contacts.router)
router.include_router(payments.router)
router.include_router(admin.router)
