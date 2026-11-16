import re

import httpx

from app.core.config import settings
from app.services import email_service
from tests.conftest import register

API = "/api/v1"


def _token_from(mail):
    return re.search(r"token=([\w.\-]+)", mail["text"]).group(1)


# ── Notificaciones al dueño ──

def test_contact_notifies_owner(client, owner, business, outbox):
    r = client.post(f"{API}/businesses/{business['id']}/contact", json={
        "client_name": "Ana <b>López</b>", "client_phone": "3001112233", "client_email": "ana@cliente.co",
        "message": "Necesito un servicio\n<script>alert(1)</script>",
    })
    assert r.status_code == 201
    assert len(outbox) == 1
    mail = outbox[0]
    assert mail["to"] == "dueno@test.co" and mail["reply_to"] == "ana@cliente.co"
    assert "Taller El Rápido" in mail["subject"]
    assert "3001112233" in mail["text"] and "/dashboard" in mail["text"]
    # Lo que escribe el cliente nunca llega como HTML ejecutable
    assert "<script>" not in mail["html"] and "&lt;script&gt;" in mail["html"]
    assert "<b>López</b>" not in mail["html"]


def test_review_notifies_owner(client, owner, business, outbox):
    url = f"{API}/businesses/{business['id']}/reviews"
    assert client.post(url, json={"author_name": "Luis", "rating": 4, "comment": "Buen servicio"}).status_code == 201
    assert len(outbox) == 1
    assert outbox[0]["to"] == "dueno@test.co" and "★★★★☆" in outbox[0]["text"]


def test_email_failure_does_not_break_the_request(client, owner, business, monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_PROVIDER", "resend")
    monkeypatch.setattr(settings, "EMAIL_API_KEY", "re_test")
    monkeypatch.setattr(settings, "EMAIL_FROM", "ServiciosBogotá <no-reply@test.co>")

    def boom(*args, **kwargs):
        raise httpx.ConnectError("sin red")

    monkeypatch.setattr(email_service.httpx, "post", boom)
    r = client.post(f"{API}/businesses/{business['id']}/contact", json={
        "client_name": "Ana", "client_phone": "3001112233", "message": "Necesito un servicio",
    })
    assert r.status_code == 201


def test_provider_payloads(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            pass

    def fake_post(url, headers, json, timeout):
        calls.append((url, headers, json))
        return FakeResponse()

    monkeypatch.setattr(email_service.httpx, "post", fake_post)
    monkeypatch.setattr(settings, "EMAIL_API_KEY", "clave")
    monkeypatch.setattr(settings, "EMAIL_FROM", "ServiciosBogotá <hola@test.co>")

    monkeypatch.setattr(settings, "EMAIL_PROVIDER", "resend")
    assert email_service.send_email("a@b.co", "Asunto", "<p>x</p>", "x", reply_to="c@d.co") is True
    url, headers, body = calls[-1]
    assert url == "https://api.resend.com/emails" and headers["Authorization"] == "Bearer clave"
    assert body["from"] == "ServiciosBogotá <hola@test.co>" and body["to"] == ["a@b.co"] and body["reply_to"] == "c@d.co"

    monkeypatch.setattr(settings, "EMAIL_PROVIDER", "brevo")
    assert email_service.send_email("a@b.co", "Asunto", "<p>x</p>", "x") is True
    url, headers, body = calls[-1]
    assert url == "https://api.brevo.com/v3/smtp/email" and headers["api-key"] == "clave"
    assert body["sender"] == {"name": "ServiciosBogotá", "email": "hola@test.co"}
    assert body["to"] == [{"email": "a@b.co"}] and body["htmlContent"] == "<p>x</p>" and "replyTo" not in body


# ── Recuperación de contraseña ──

def test_password_reset_flow(client, outbox):
    register(client, email="ana@test.co", password="Password123", name="Ana Ruiz")

    # Un correo que no existe responde igual y no envía nada
    r = client.post(f"{API}/auth/forgot-password", json={"email": "nadie@test.co"})
    assert r.status_code == 200 and outbox == []

    r2 = client.post(f"{API}/auth/forgot-password", json={"email": "ANA@test.co"})
    assert r2.status_code == 200 and r2.json() == r.json()
    assert len(outbox) == 1 and outbox[0]["to"] == "ana@test.co"
    assert "http://localhost:5173/restablecer?token=" in outbox[0]["text"]
    token = _token_from(outbox[0])

    assert client.post(f"{API}/auth/reset-password", json={"token": token, "new_password": "corta"}).status_code == 422
    assert client.post(f"{API}/auth/reset-password", json={"token": token, "new_password": "NuevaClave456"}).status_code == 204
    assert client.post(f"{API}/auth/login", json={"email": "ana@test.co", "password": "NuevaClave456"}).status_code == 200
    assert client.post(f"{API}/auth/login", json={"email": "ana@test.co", "password": "Password123"}).status_code == 401

    # El enlace es de un solo uso
    r = client.post(f"{API}/auth/reset-password", json={"token": token, "new_password": "OtraClave789"})
    assert r.status_code == 400


def test_reset_rejects_other_token_types(client):
    r = client.post(f"{API}/auth/register", json={"email": "a@test.co", "password": "Password123", "full_name": "A"})
    for token in (r.json()["access_token"], r.json()["refresh_token"], "no-es-un-token"):
        r2 = client.post(f"{API}/auth/reset-password", json={"token": token, "new_password": "NuevaClave456"})
        assert r2.status_code == 400
    # Y un token de restablecimiento no sirve para iniciar sesión
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": "x"}).status_code == 401
