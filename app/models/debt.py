import uuid
import enum
from datetime import date, datetime, timezone

from sqlalchemy import String, Integer, Date, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class DebtStatus(str, enum.Enum):
    active = "active"
    paid = "paid"
    late = "late"


class DebtSource(str, enum.Enum):
    screenshot = "screenshot"
    manual = "manual"


class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="Amount in Rupiah")
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    installment_current: Mapped[int] = mapped_column(Integer, nullable=True)
    installment_total: Mapped[int] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[DebtStatus] = mapped_column(SAEnum(DebtStatus), default=DebtStatus.active)
    source: Mapped[DebtSource] = mapped_column(SAEnum(DebtSource), default=DebtSource.manual)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="debts")
    reminders = relationship("Reminder", back_populates="debt", cascade="all, delete-orphan")
