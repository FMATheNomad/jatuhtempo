import os

from app.models.user import User


def is_admin(user: User) -> bool:
    admin_emails = os.environ.get("ADMIN_EMAILS", "")
    if admin_emails and user.email and user.email in [e.strip() for e in admin_emails.split(",")]:
        return True
    return False
