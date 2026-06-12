from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, JSON, DateTime
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
    type_counts: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    rate_std: Mapped[float] = mapped_column(Float, default=0.0, comment="Running std dev via Welford's")
    min_rate: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Minimum rate observed")
    max_rate: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Maximum rate observed")
    last_rate_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    outlier_count: Mapped[int] = mapped_column(Integer, default=0)
