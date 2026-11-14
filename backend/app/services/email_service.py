"""
Correo transaccional.

Se envía por la API HTTPS del proveedor (Resend o Brevo), no por SMTP: Railway
bloquea los puertos SMTP en los planes Free y Hobby. Un fallo de correo nunca
debe tumbar la petición que lo originó: se registra en el log y se sigue.
"""
import logging
from email.utils import parseaddr
from html import escape
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("serviciosbogota.email")

BRAND = "#F5A623"


def _post(url: str, headers: dict, payload: dict) -> None:
    response = httpx.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()


def _send_resend(to: str, subject: str, html: str, text: str, reply_to: Optional[str]) -> None:
    payload = {"from": settings.EMAIL_FROM, "to": [to], "subject": subject, "html": html, "text": text}
    if reply_to:
        payload["reply_to"] = reply_to
    _post("https://api.resend.com/emails", {"Authorization": f"Bearer {settings.EMAIL_API_KEY}"}, payload)


def _send_brevo(to: str, subject: str, html: str, text: str, reply_to: Optional[str]) -> None:
    name, address = parseaddr(settings.EMAIL_FROM)
    payload = {
        "sender": {"name": name or settings.APP_NAME, "email": address},
        "to": [{"email": to}],
        "subject": subject,
        "htmlContent": html,
        "textContent": text,
    }
    if reply_to:
        payload["replyTo"] = {"email": reply_to}
    _post("https://api.brevo.com/v3/smtp/email", {"api-key": settings.EMAIL_API_KEY}, payload)


def send_email(to: str, subject: str, html: str, text: str, reply_to: Optional[str] = None) -> bool:
    """Envía un correo. Devuelve False (sin lanzar error) si no se pudo enviar."""
    if not settings.email_enabled:
        # En desarrollo el contenido queda en el log para poder probar los flujos.
        logger.warning("Correo no configurado. Para: %s | Asunto: %s\n%s", to, subject, text)
        return False
    try:
        sender = _send_brevo if settings.EMAIL_PROVIDER.lower() == "brevo" else _send_resend
        sender(to, subject, html, text, reply_to)
        return True
    except Exception:
        logger.exception("No se pudo enviar el correo a %s (%s)", to, subject)
        return False


def _layout(title: str, body_html: str, button: Optional[tuple] = None) -> str:
    button_html = ""
    if button:
        label, url = button
        button_html = (
            f'<p style="margin:28px 0"><a href="{escape(url, quote=True)}" '
            f'style="background:{BRAND};color:#000;font-weight:bold;text-decoration:none;'
            f'padding:12px 22px;border-radius:8px;display:inline-block">{escape(label)}</a></p>'
        )
    return (
        '<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:0 auto;'
        'padding:24px;color:#18181b">'
        f'<p style="font-size:18px;font-weight:bold;margin:0 0 20px">Servicios<span style="color:{BRAND}">Bogotá</span></p>'
        f'<h1 style="font-size:20px;margin:0 0 16px">{escape(title)}</h1>'
        f"{body_html}{button_html}"
        '<p style="color:#71717a;font-size:12px;margin-top:32px;border-top:1px solid #e4e4e7;padding-top:12px">'
        "Recibes este correo porque tienes una cuenta en ServiciosBogotá.</p></div>"
    )


def _frontend(path: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


def _quote(text: str) -> str:
    safe = escape(text).replace("\n", "<br>")
    return (
        f'<blockquote style="margin:16px 0;padding:12px 16px;background:#f4f4f5;'
        f'border-left:4px solid {BRAND}">{safe}</blockquote>'
    )


def send_new_contact_email(
    owner_email: str,
    business_name: str,
    client_name: str,
    message: str,
    client_phone: Optional[str] = None,
    client_email: Optional[str] = None,
) -> bool:
    """Avisa al dueño que un cliente dejó una solicitud en su perfil."""
    contact_lines = []
    if client_phone:
        contact_lines.append(f"Teléfono: {client_phone}")
    if client_email:
        contact_lines.append(f"Correo: {client_email}")
    dashboard = _frontend("/dashboard")

    html = _layout(
        f"Nueva solicitud para {business_name}",
        f"<p><strong>{escape(client_name)}</strong> te escribió desde tu perfil:</p>"
        f"{_quote(message)}"
        + "".join(f'<p style="margin:4px 0">{escape(line)}</p>' for line in contact_lines)
        + '<p style="margin-top:16px">Responde pronto: los clientes suelen escribir a varios negocios a la vez.</p>',
        ("Ver la solicitud", dashboard),
    )
    text = (
        f"Nueva solicitud para {business_name}\n\n"
        f"{client_name} te escribió desde tu perfil:\n\n{message}\n\n"
        + "\n".join(contact_lines)
        + f"\n\nVer la solicitud: {dashboard}"
    )
    return send_email(
        owner_email,
        f"Nueva solicitud de {client_name} · {business_name}",
        html,
        text,
        reply_to=client_email,
    )


def send_new_review_email(
    owner_email: str,
    business_name: str,
    business_slug: str,
    author_name: str,
    rating: float,
    comment: Optional[str] = None,
) -> bool:
    """Avisa al dueño que recibió una reseña, para que pueda responderla."""
    stars = "★" * round(rating) + "☆" * (5 - round(rating))
    dashboard = _frontend("/dashboard")
    html = _layout(
        f"Nueva reseña para {business_name}",
        f'<p><strong>{escape(author_name)}</strong> calificó tu negocio: '
        f'<span style="color:{BRAND};font-size:18px">{stars}</span></p>'
        + (_quote(comment) if comment else "")
        + "<p>Responder las reseñas (también las negativas) genera confianza en quienes visitan tu perfil.</p>",
        ("Responder la reseña", dashboard),
    )
    text = (
        f"Nueva reseña para {business_name}\n\n{author_name} calificó tu negocio: {stars}\n"
        + (f"\n{comment}\n" if comment else "")
        + f"\nResponder: {dashboard}\nPerfil público: {_frontend('/negocio/' + business_slug)}"
    )
    return send_email(owner_email, f"{author_name} dejó una reseña · {business_name}", html, text)


def send_password_reset_email(to: str, full_name: str, token: str) -> bool:
    link = _frontend(f"/restablecer?token={token}")
    minutes = settings.PASSWORD_RESET_EXPIRE_MINUTES
    first_name = full_name.split(" ")[0] if full_name else ""
    html = _layout(
        "Restablece tu contraseña",
        f"<p>Hola {escape(first_name)}, recibimos una solicitud para cambiar la contraseña de tu cuenta.</p>"
        f"<p>El enlace vence en {minutes} minutos y solo se puede usar una vez.</p>",
        ("Crear nueva contraseña", link),
    ) + (
        '<p style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;padding:0 24px;'
        'color:#71717a;font-size:12px">Si no fuiste tú, ignora este correo: tu contraseña no cambia.</p>'
    )
    text = (
        f"Hola {first_name}, recibimos una solicitud para cambiar tu contraseña.\n\n"
        f"Abre este enlace (vence en {minutes} minutos): {link}\n\n"
        "Si no fuiste tú, ignora este correo: tu contraseña no cambia."
    )
    return send_email(to, "Restablece tu contraseña de ServiciosBogotá", html, text)
