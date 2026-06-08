import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_audit(
    session: AsyncSession,
    user_id: uuid.UUID | None,
    action: str,
    resource: str,
    resource_id: str | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        detail=detail,
        ip_address=ip_address,
    )
    session.add(entry)
    await session.commit()
