import hashlib
from datetime import timedelta

from app.db.database import SessionLocal
from app.models.subscription import Subscription, SubscriptionStatus
from app.services import wompi_service
from app.services.subscription_service import _utcnow, expire_subscriptions
from tests.conftest import BUSINESS, register

API = "/api/v1"


# ── Arranque y catálogos ──

def test_startup_seeds_categories_and_admin(client, admin):
    cats = client.get(f"{API}/categories").json()
    assert len(cats) == 12 and cats[0]["slug"] == "mecanica"
    assert client.get(f"{API}/admin/stats", headers=admin).status_code == 200
    assert len(client.get(f"{API}/localidades").json()) == 20


def test_list_routes_do_not_redirect(client):
    # Una redirección 307 aquí es la causa del error de contenido mixto en producción.
    for path in ("/businesses", "/categories", "/businesses/1/reviews"):
        assert client.get(f"{API}{path}", follow_redirects=False).status_code == 200


# ── Auth ──

def test_register_login_me(client):
    headers = register(client, email="Ana@Test.co")
    me = client.get(f"{API}/auth/me", headers=headers).json()
    assert me["email"] == "ana@test.co" and me["role"] == "business_owner"
    dup = client.post(f"{API}/auth/register", json={"email": "ana@test.co", "password": "Password123", "full_name": "x"})
    assert dup.status_code == 409
    bad = client.post(f"{API}/auth/login", json={"email": "ana@test.co", "password": "incorrecta"})
    assert bad.status_code == 401
    assert client.get(f"{API}/auth/me").status_code in (401, 403)


def test_refresh_and_change_password(client):
    r = client.post(f"{API}/auth/register", json={"email": "a@test.co", "password": "Password123", "full_name": "A"})
    tokens = r.json()
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 200
    # Un access token no sirve como refresh token
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": tokens["access_token"]}).status_code == 401
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.post(f"{API}/auth/change-password", headers=headers,
                    json={"current_password": "Password123", "new_password": "NuevaClave456"})
    assert r.status_code == 204
    assert client.post(f"{API}/auth/login", json={"email": "a@test.co", "password": "NuevaClave456"}).status_code == 200


# ── Negocios ──

def test_business_crud_and_search(client, owner, business):
    assert business["slug"] == "taller-el-rapido" and business["email"] is None
    assert client.post(f"{API}/businesses", json=BUSINESS, headers=owner).json()["slug"] == "taller-el-rapido-1"

    assert client.get(f"{API}/businesses", params={"search": "frenos"}).json()["total"] == 2
    assert client.get(f"{API}/businesses", params={"search": "mecánica"}).json()["total"] == 2  # por categoría
    assert client.get(f"{API}/businesses", params={"category": "belleza"}).json()["total"] == 0
    assert client.get(f"{API}/businesses", params={"localidad": "Suba", "sort": "recent"}).json()["total"] == 2

    r = client.put(f"{API}/businesses/{business['id']}", headers=owner, json={
        "short_description": "Nuevo texto", "website": "taller.co",
        "schedule": {"lunes": {"open": "08:00", "close": "18:00", "closed": False}},
    })
    assert r.status_code == 200
    assert r.json()["website"] == "https://taller.co" and r.json()["schedule"]["lunes"]["open"] == "08:00"

    other = register(client, email="otro@test.co")
    assert client.put(f"{API}/businesses/{business['id']}", headers=other, json={"name": "Hack"}).status_code == 404
    assert client.delete(f"{API}/businesses/{business['id']}", headers=other).status_code == 404
    assert client.delete(f"{API}/businesses/{business['id']}", headers=owner).status_code == 204
    assert client.get(f"{API}/businesses/{business['slug']}").status_code == 404


def test_business_validation(client, owner):
    assert client.post(f"{API}/businesses", json={**BUSINESS, "localidad": "Medellín"}, headers=owner).status_code == 422
    assert client.post(f"{API}/businesses", json={**BUSINESS, "category_id": 999}, headers=owner).status_code == 400
    assert client.post(f"{API}/businesses", json={**BUSINESS, "phone": "12"}, headers=owner).status_code == 422
    assert client.post(f"{API}/businesses", json=BUSINESS).status_code in (401, 403)


def test_views_count_only_visitors(client, owner, business):
    client.get(f"{API}/businesses/{business['slug']}")
    client.get(f"{API}/businesses/{business['slug']}", headers=owner)
    assert client.get(f"{API}/businesses/my", headers=owner).json()[0]["view_count"] == 1


def test_upload_without_cloudinary_returns_503(client, owner, business):
    r = client.post(f"{API}/businesses/{business['id']}/logo", headers=owner,
                    files={"file": ("logo.png", b"fake", "image/png")})
    assert r.status_code == 503


# ── Reseñas y contactos ──

def test_reviews_flow(client, owner, business, admin):
    url = f"{API}/businesses/{business['id']}/reviews"
    assert client.post(url, json={"author_name": "Luis", "rating": 9}).status_code == 422
    assert client.post(url, json={"author_name": "Dueño", "rating": 5}, headers=owner).status_code == 403

    review = client.post(url, json={"author_name": "Luis", "rating": 4, "comment": "Buen servicio"}).json()
    client.post(url, json={"author_name": "Marta", "rating": 5})
    detail = client.get(f"{API}/businesses/{business['slug']}").json()
    assert detail["rating_avg"] == 4.5 and detail["rating_count"] == 2

    cliente = register(client, email="cliente@test.co")
    assert client.post(url, json={"author_name": "Cli", "rating": 5}, headers=cliente).status_code == 201
    assert client.post(url, json={"author_name": "Cli", "rating": 5}, headers=cliente).status_code == 409

    r = client.put(f"{url}/{review['id']}/response", json={"response": "¡Gracias!"}, headers=owner)
    assert r.status_code == 200 and r.json()["response"] == "¡Gracias!"
    assert client.put(f"{url}/{review['id']}/response", json={"response": "x2"}, headers=cliente).status_code == 404

    # El admin oculta una reseña y la calificación se recalcula
    r = client.patch(f"{API}/admin/reviews/{review['id']}/visibility", params={"visible": False}, headers=admin)
    assert r.status_code == 200
    assert len(client.get(url).json()) == 2
    assert client.get(f"{API}/businesses/{business['slug']}").json()["rating_avg"] == 5.0


def test_contacts_flow(client, owner, business):
    url = f"{API}/businesses/{business['id']}/contact"
    assert client.post(url, json={"client_name": "Ana", "message": "Necesito un servicio"}).status_code == 422
    r = client.post(url, json={"client_name": "Ana", "client_phone": "3001112233", "client_email": "",
                               "message": "Necesito un servicio"})
    assert r.status_code == 201
    contact_id = r.json()["id"]

    mine = f"{API}/my-businesses/{business['id']}/contacts"
    assert client.get(mine, headers=owner).json()[0]["status"] == "new"
    r = client.patch(f"{mine}/{contact_id}", json={"status": "replied"}, headers=owner)
    assert r.json()["status"] == "replied"
    other = register(client, email="otro@test.co")
    assert client.get(mine, headers=other).status_code == 404
    assert client.get(f"{API}/businesses/my", headers=owner).json()[0]["contact_count"] == 1


# ── Pagos ──

def _event(reference, status="APPROVED", amount=6500000, tx_id="tx-1", secret="test_events_secret"):
    event = {
        "event": "transaction.updated",
        "data": {"transaction": {"id": tx_id, "status": status, "amount_in_cents": amount,
                                 "reference": reference, "currency": "COP"}},
        "signature": {"properties": ["transaction.id", "transaction.status", "transaction.amount_in_cents"]},
        "timestamp": 1530291411,
    }
    raw = f"{tx_id}{status}{amount}1530291411{secret}"
    event["signature"]["checksum"] = hashlib.sha256(raw.encode()).hexdigest()
    return event


def test_event_checksum_matches_wompi_documentation():
    # Ejemplo publicado en la documentación de eventos de Wompi.
    event = {
        "data": {"transaction": {"id": "1234-1610641025-49201", "status": "APPROVED", "amount_in_cents": 4490000}},
        "signature": {"properties": ["transaction.id", "transaction.status", "transaction.amount_in_cents"]},
        "timestamp": 1530291411,
    }
    secret = "prod_events_OcHnIzeBl5socpwByQ4hA52Em3USQ93Z"
    raw = "1234-1610641025-49201APPROVED44900001530291411" + secret
    assert wompi_service.event_checksum(event, secret) == hashlib.sha256(raw.encode()).hexdigest()


def test_checkout_requires_ownership_and_signs(client, owner, business):
    r = client.post(f"{API}/payments/checkout", headers=owner, json={"business_id": business["id"], "plan": "premium"})
    assert r.status_code == 200
    data = r.json()
    assert data["amount_in_cents"] == 6500000
    expected = hashlib.sha256(f"{data['reference']}6500000COPtest_integrity_secret".encode()).hexdigest()
    assert f"signature%3Aintegrity={expected}" in data["checkout_url"]
    assert "redirect-url=http%3A%2F%2Flocalhost%3A5173%2Fpago%2Fconfirmacion" in data["checkout_url"]

    other = register(client, email="otro@test.co")
    r = client.post(f"{API}/payments/checkout", headers=other, json={"business_id": business["id"], "plan": "basic"})
    assert r.status_code == 404


def test_webhook_activates_plan_once(client, owner, business):
    ref = f"svc-{business['id']}-premium-1700000000"
    bad = _event(ref, secret="otro_secreto")
    assert client.post(f"{API}/payments/wompi-webhook", json=bad).status_code == 400

    # Monto alterado: firma válida pero no corresponde al plan
    r = client.post(f"{API}/payments/wompi-webhook", json=_event(ref, amount=100))
    assert r.json() == {"status": "processed", "activated": False}
    assert client.get(f"{API}/businesses/my", headers=owner).json()[0]["subscription"] is None

    assert client.post(f"{API}/payments/wompi-webhook", json=_event(ref)).json()["activated"] is True
    first = client.get(f"{API}/businesses/my", headers=owner).json()[0]
    assert first["subscription"]["plan"] == "premium" and first["subscription"]["status"] == "active"
    assert first["is_featured"] is True

    # El mismo evento repetido no extiende la suscripción
    client.post(f"{API}/payments/wompi-webhook", json=_event(ref))
    again = client.get(f"{API}/businesses/my", headers=owner).json()[0]
    assert again["subscription"]["expires_at"] == first["subscription"]["expires_at"]

    # Una renovación (otra transacción) suma 30 días
    client.post(f"{API}/payments/wompi-webhook", json=_event(ref, tx_id="tx-2"))
    renewed = client.get(f"{API}/businesses/my", headers=owner).json()[0]
    assert renewed["subscription"]["expires_at"] > first["subscription"]["expires_at"]

    declined = _event(f"svc-{business['id']}-basic-1700000001", status="DECLINED", amount=2500000, tx_id="tx-3")
    assert client.post(f"{API}/payments/wompi-webhook", json=declined).json()["activated"] is False


def test_verify_transaction_activates(client, owner, business, monkeypatch):
    monkeypatch.setattr(wompi_service, "fetch_transaction", lambda tx_id: {
        "id": tx_id, "status": "APPROVED", "amount_in_cents": 2500000, "currency": "COP",
        "reference": f"svc-{business['id']}-basic-1700000000",
    })
    r = client.get(f"{API}/payments/verify/tx-99")
    assert r.json()["status"] == "APPROVED" and r.json()["activated"] is True and r.json()["plan"] == "basic"
    mine = client.get(f"{API}/businesses/my", headers=owner).json()[0]
    assert mine["subscription"]["plan"] == "basic" and mine["is_featured"] is False


def test_subscription_expiration(client, owner, business, admin):
    r = client.post(f"{API}/admin/businesses/{business['id']}/subscription", headers=admin,
                    json={"plan": "premium", "days": 30})
    assert r.status_code == 200
    db = SessionLocal()
    try:
        sub = db.query(Subscription).filter_by(business_id=business["id"]).one()
        sub.expires_at = _utcnow() - timedelta(days=1)
        db.commit()
        assert expire_subscriptions(db) == 1
        assert db.query(Subscription).one().status == SubscriptionStatus.expired
    finally:
        db.close()
    mine = client.get(f"{API}/businesses/my", headers=owner).json()[0]
    assert mine["subscription"]["status"] == "expired" and mine["is_featured"] is False
    assert mine["status"] == "active"  # el perfil sigue visible, solo pierde los beneficios


# ── Admin ──

def test_admin_moderation(client, owner, business, admin):
    assert client.get(f"{API}/admin/stats", headers=owner).status_code == 403
    listing = client.get(f"{API}/admin/businesses", headers=admin).json()
    assert listing["total"] == 1 and listing["items"][0]["owner_email"] == "dueno@test.co"

    assert client.patch(f"{API}/admin/businesses/{business['id']}/suspend", headers=admin).status_code == 200
    assert client.get(f"{API}/businesses").json()["total"] == 0
    assert client.get(f"{API}/businesses/{business['slug']}").status_code == 404
    # El dueño sí puede seguir viendo su negocio suspendido
    assert client.get(f"{API}/businesses/{business['slug']}", headers=owner).status_code == 200

    client.patch(f"{API}/admin/businesses/{business['id']}/approve", headers=admin)
    client.patch(f"{API}/admin/businesses/{business['id']}/featured", params={"featured": True}, headers=admin)
    assert client.get(f"{API}/businesses", params={"featured": True}).json()["total"] == 1
    assert client.get(f"{API}/stats").json()["businesses"] == 1
    assert len(client.get(f"{API}/admin/users", headers=admin).json()) == 2
