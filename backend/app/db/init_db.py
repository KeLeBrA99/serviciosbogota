"""
Script para inicializar la base de datos con datos semilla.
Ejecutar una sola vez: python -m app.db.init_db
"""
from sqlalchemy.orm import Session
from app.db.database import engine, Base, SessionLocal
from app.models import Category, User, UserRole
from app.core.security import hash_password


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")


def seed_categories(db: Session):
    categories = [
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
    for cat_data in categories:
        existing = db.query(Category).filter_by(slug=cat_data["slug"]).first()
        if not existing:
            db.add(Category(**cat_data))
    db.commit()
    print(f"✅ {len(categories)} categorías creadas")


def seed_admin(db: Session):
    existing = db.query(User).filter_by(email="admin@serviciosbogota.co").first()
    if not existing:
        admin = User(
            email="admin@serviciosbogota.co",
            hashed_password=hash_password("Admin2024!"),
            full_name="Admin ServiciosBogotá",
            role=UserRole.admin,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        print("✅ Admin creado: admin@serviciosbogota.co / Admin2024!")
    else:
        print("⚠️  Admin ya existe")


def init():
    create_tables()
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_admin(db)
        print("\n🚀 Base de datos lista")
    finally:
        db.close()


if __name__ == "__main__":
    init()
