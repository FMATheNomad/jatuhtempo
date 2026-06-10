from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PlatformRate(Base):
    """Aggregated interest rate data per platform, learned from user input."""
    __tablename__ = "platform_rates"

    platform: Mapped[str] = mapped_column(String(100), primary_key=True)
    avg_rate: Mapped[float] = mapped_column(Float, default=0.0)
    common_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
