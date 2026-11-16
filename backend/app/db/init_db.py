"""
Datos semilla de la base de datos.

Se ejecuta automáticamente al arrancar la API (es idempotente) y también se
puede correr a mano:  python -m app.db.init_db
"""
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.db.migrations import run_migrations
from app.models import Category, User, UserRole

DEFAULT_CATEGORIES = [
    {"name": "Mecánica", "slug": "mecanica", "icon": "🔧", "sort_order": 1},
    {"name": "Belleza", "slug": "belleza", "icon": "✂️", "sort_order": 2},
    {"name": "Plomería", "slug": "plomeria", "icon": "🚿", "sort_order": 3},
    {"name": "Electricidad", "slug": "electricidad", "icon": "💡", "sort_order": 4},
    {"name": "Mudanzas", "slug": "mudanzas", "icon": "📦", "sort_order": 5},
    {"name": "Limpieza", "slug": "limpieza", "icon": "🧹", "sort_order": 6},
    {"name": "Tecnología", "slug": "tecnologia", "icon": "💻", "sort_order": 7},
    {"name": "Construcción", "slug": "construccion", "icon": "🏗️", "sort_order": 8},
    {"name": "Salud", "slug": "salud", "icon": "🏥", "sort_order": 9},
    {"name": "Educación", "slug": "educacion", "icon": "📚", "sort_order": 10},
    {"name": "Mascotas", "slug": "mascotas", "icon": "🐾", "sort_order": 11},
    {"name": "Jardinería", "slug": "jardineria", "icon": "🌿", "sort_order": 12},
]


def seed_categories(db: Session) -> int:
    """Crea las categorías que falten. Devuelve cuántas se crearon."""
    existing = {slug for (slug,) in db.query(Category.slug).all()}
    created = 0
    for data in DEFAULT_CATEGORIES:
        if data["slug"] not in existing:
            db.add(Category(**data))
            created += 1
    if created:
        db.commit()
    return created


def seed_admin(db: Session) -> bool:
    """Crea el administrador inicial a partir de ADMIN_EMAIL / ADMIN_PASSWORD."""
    if not (settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD):
        return False
    email = settings.ADMIN_EMAIL.strip().lower()
    if db.query(User).filter_by(email=email).first():
        return False
    db.add(
        User(
            email=email,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name="Administrador",
            role=UserRole.admin,
            is_active=True,
            is_verified=True,
        )
    )
    db.commit()
    return True


def init():
    run_migrations()
    db = SessionLocal()
    try:
        created = seed_categories(db)
        admin_created = seed_admin(db)
    finally:
        db.close()
    print(f"Base de datos lista: {created} categorías nuevas, admin creado: {admin_created}")


if __name__ == "__main__":
    init()
