import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_reset_email(to_email: str, reset_url: str) -> bool:
    if not settings.smtp_user or not settings.smtp_pass:
        logger.warning("SMTP not configured. Reset URL: %s", reset_url)
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "JatuhTempo — Reset Password"
        msg["From"] = settings.smtp_from or settings.smtp_user
        msg["To"] = to_email

        text = f"""Halo,

Kami menerima permintaan reset password untuk akun JatuhTempo kamu.

Klik link berikut untuk mereset password:
{reset_url}

Link ini berlaku 1 jam.

Jika kamu tidak meminta reset password, abaikan email ini.

— JatuhTempo
"""
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="font-family:sans-serif;padding:24px;background:#f8fafc">
<div style="max-width:480px;margin:auto;background:white;border-radius:16px;padding:32px">
<img src="https://jatuhtempo.up.railway.app/assets/logo.webp" alt="JatuhTempo" style="height:32px;margin-bottom:24px">
<h2 style="margin:0 0 8px">Reset Password</h2>
<p style="color:#64748b;margin:0 0 24px">Klik tombol di bawah untuk mereset password akun JatuhTempo kamu.</p>
<a href="{reset_url}" style="display:inline-block;padding:12px 32px;background:#0d9488;color:white;text-decoration:none;border-radius:12px;font-weight:600">Reset Password</a>
<p style="color:#94a3b8;font-size:12px;margin-top:24px">Link berlaku 1 jam. Abaikan jika kamu tidak meminta reset.</p>
</div></body></html>"""

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_from or settings.smtp_user, [to_email], msg.as_string())

        logger.info("Reset email sent to %s", to_email)
        return True

    except Exception as e:
        logger.exception("Failed to send reset email to %s: %s", to_email, e)
        return False
