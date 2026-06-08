import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, unique=True, index=True)
    nama: Mapped[str] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    wa_linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    wa_reminder_optout: Mapped[bool] = mapped_column(Boolean, default=False)
    polar_customer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subscription_status: Mapped[str] = mapped_column(String(20), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    debts = relationship("Debt", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
