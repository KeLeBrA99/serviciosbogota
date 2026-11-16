from datetime import timedelta

from app.db.database import SessionLocal
from app.models.event import BusinessEvent
from app.models.subscription import Subscription, SubscriptionStatus
from app.services.subscription_service import (
    _utcnow,
    expire_subscriptions,
    run_subscription_sweep,
    send_expiry_reminders,
)
from tests.conftest import register

API = "/api/v1"


def _set_expiry(business_id, delta):
    db = SessionLocal()
    try:
        sub = db.query(Subscription).filter_by(business_id=business_id).one()
        sub.expires_at = _utcnow() + delta
        db.commit()
    finally:
        db.close()


def _activate(client, admin, business_id, plan="premium"):
    r = client.post(f"{API}/admin/businesses/{business_id}/subscription", headers=admin, json={"plan": plan, "days": 30})
    assert r.status_code == 200


# ── Clics en WhatsApp y llamada ──

def test_click_tracking_and_stats(client, owner, business, admin):
    track = f"{API}/businesses/{business['id']}/track"
    for kind in ("whatsapp", "whatsapp", "call"):
        assert client.post(track, json={"type": kind}).status_code == 204
    assert client.post(track, json={"type": "otro"}).status_code == 422
    assert client.post(f"{API}/businesses/999/track", json={"type": "call"}).status_code == 404

    # Los clics del dueño y del admin no inflan las cifras
    assert client.post(track, json={"type": "whatsapp"}, headers=owner).status_code == 204
    assert client.post(track, json={"type": "whatsapp"}, headers=admin).status_code == 204

    client.post(f"{API}/businesses/{business['id']}/contact",
                json={"client_name": "Ana", "client_phone": "3001112233", "message": "Necesito un servicio"})
    client.post(f"{API}/businesses/{business['id']}/reviews", json={"author_name": "Luis", "rating": 5})

    # Un clic de hace dos meses queda fuera del periodo
    db = SessionLocal()
    try:
        db.add(BusinessEvent(business_id=business["id"], type="call", created_at=_utcnow() - timedelta(days=60)))
        db.commit()
    finally:
        db.close()

    stats_url = f"{API}/businesses/{business['id']}/stats"
    assert client.get(stats_url, headers=owner).json() == {
        "days": 30, "whatsapp_clicks": 2, "call_clicks": 1, "contacts": 1, "reviews": 1,
    }
    other = register(client, email="otro@test.co")
    assert client.get(stats_url, headers=other).status_code == 404
    assert client.get(stats_url).status_code in (401, 403)


def test_suspended_business_is_not_tracked_and_delete_removes_events(client, owner, business, admin):
    track = f"{API}/businesses/{business['id']}/track"
    client.post(track, json={"type": "call"})
    client.patch(f"{API}/admin/businesses/{business['id']}/suspend", headers=admin)
    assert client.post(track, json={"type": "call"}).status_code == 404
    assert client.delete(f"{API}/businesses/{business['id']}", headers=owner).status_code == 204
    db = SessionLocal()
    try:
        assert db.query(BusinessEvent).count() == 0
    finally:
        db.close()


# ── Avisos de vencimiento ──

def test_expiry_reminder_is_sent_once(client, owner, business, admin, outbox):
    _activate(client, admin, business["id"])
    db = SessionLocal()
    try:
        assert send_expiry_reminders(db) == 0  # faltan 30 días: todavía no
        _set_expiry(business["id"], timedelta(days=3, hours=2))
        assert send_expiry_reminders(db) == 1
        assert send_expiry_reminders(db) == 0  # no se repite
    finally:
        db.close()
    assert len(outbox) == 1
    mail = outbox[0]
    assert mail["to"] == "dueno@test.co"
    assert mail["subject"] == "Tu plan Premium vence en 3 días · Taller El Rápido"
    assert f"/planes?negocio={business['id']}" in mail["text"]


def test_renewal_rearms_the_reminder(client, owner, business, admin, outbox):
    _activate(client, admin, business["id"])
    _set_expiry(business["id"], timedelta(days=1, hours=1))
    db = SessionLocal()
    try:
        assert send_expiry_reminders(db) == 1
        assert "vence mañana" in outbox[0]["subject"]
        _activate(client, admin, business["id"])  # renueva: quedan 31 días
        assert send_expiry_reminders(db) == 0
        _set_expiry(business["id"], timedelta(days=2))
        db.expire_all()
        assert send_expiry_reminders(db) == 1  # el nuevo periodo recibe su propio aviso
    finally:
        db.close()
    assert len(outbox) == 2


def test_failed_reminder_is_retried(client, owner, business, admin, monkeypatch):
    from app.core.config import settings
    from app.services import email_service

    _activate(client, admin, business["id"], plan="basic")
    _set_expiry(business["id"], timedelta(days=2))
    monkeypatch.setattr(settings, "EMAIL_PROVIDER", "resend")
    monkeypatch.setattr(settings, "EMAIL_API_KEY", "re_test")
    monkeypatch.setattr(settings, "EMAIL_FROM", "x <x@test.co>")
    results = iter([False, True])
    monkeypatch.setattr(email_service, "send_email", lambda *a, **k: next(results))
    db = SessionLocal()
    try:
        assert send_expiry_reminders(db) == 0  # el proveedor falló: queda pendiente
        assert send_expiry_reminders(db) == 1
    finally:
        db.close()


def test_expired_plan_notifies_owner(client, owner, business, admin, outbox):
    _activate(client, admin, business["id"])
    _set_expiry(business["id"], timedelta(hours=-1))
    db = SessionLocal()
    try:
        assert run_subscription_sweep(db) == {"expired": 1, "reminders": 0}
        assert expire_subscriptions(db) == 0
        assert db.query(Subscription).one().status == SubscriptionStatus.expired
    finally:
        db.close()
    assert len(outbox) == 1 and outbox[0]["subject"] == "Tu plan Premium venció · Taller El Rápido"
    assert client.post(f"{API}/admin/subscriptions/expire", headers=admin).json() == {"expired": 0, "reminders": 0}
