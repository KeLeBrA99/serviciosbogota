import os
import tempfile

# La configuración se fija antes de importar la app.
_db_file = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ.update(
    DATABASE_URL=f"sqlite:///{_db_file}",
    SECRET_KEY="clave-de-pruebas",
    APP_ENV="test",
    FRONTEND_URL="http://localhost:5173",
    WOMPI_PUBLIC_KEY="pub_test_abc123",
    WOMPI_EVENTS_SECRET="test_events_secret",
    WOMPI_INTEGRITY_SECRET="test_integrity_secret",
    CLOUDINARY_CLOUD_NAME="",
    EMAIL_PROVIDER="",
    ADMIN_EMAIL="admin@test.co",
    ADMIN_PASSWORD="AdminPass123",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.limiter import limiter
from app.db.database import Base, engine
from main import app

limiter.enabled = False

BUSINESS = {
    "name": "Taller El Rápido",
    "category_id": 1,
    "description": "Mecánica general, frenos y cambio de aceite a domicilio.",
    "short_description": "Mecánica a domicilio",
    "phone": "300 123 4567",
    "whatsapp": "300 123 4567",
    "email": "",
    "localidad": "Suba",
    "tags": ["Domicilio", "24h"],
}


def reset_database():
    Base.metadata.drop_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))


@pytest.fixture()
def client():
    reset_database()
    with TestClient(app) as c:  # el lifespan aplica las migraciones y los datos semilla
        yield c


def register(client, email="dueno@test.co", password="Password123", name="Dueño"):
    r = client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": name})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def login(client, email, password):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def owner(client):
    return register(client)


@pytest.fixture()
def admin(client):
    return login(client, "admin@test.co", "AdminPass123")


@pytest.fixture()
def business(client, owner):
    r = client.post("/api/v1/businesses", json=BUSINESS, headers=owner)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def outbox(monkeypatch):
    """Captura los correos en vez de enviarlos."""
    from app.services import email_service

    sent = []

    def fake_send(to, subject, html, text, reply_to=None):
        sent.append({"to": to, "subject": subject, "html": html, "text": text, "reply_to": reply_to})
        return True

    monkeypatch.setattr(email_service, "send_email", fake_send)
    return sent
