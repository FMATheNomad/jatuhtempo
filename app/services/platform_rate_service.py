import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.platform_rate import PlatformRate

logger = logging.getLogger(__name__)


async def update_platform_rate(
    session: AsyncSession, platform: str, rate: float, rate_type: str | None
) -> PlatformRate | None:
    """Upsert platform rate with EMA decay, outlier detection, and majority vote.

    - Outlier detection: rejects rate > 50 or rate < 0.1
    - EMA formula: new_avg = (1 - alpha) * old_avg + alpha * new_rate
      alpha = min(0.3, 1.0 / (sample_count + 1))
    - Majority vote for common_type tracked in type_counts JSON
    - Confidence = min(1.0, sample_count / 20)

    Returns None if the rate is rejected as an outlier.
    """
    # --- Outlier detection ---
    if rate > settings.platform_rate_outlier_max or rate < settings.platform_rate_outlier_min:
        logger.warning(
            "Outlier rate rejected for platform=%s: %.4f (must be %.1f–%.1f)",
            platform, rate, settings.platform_rate_outlier_min, settings.platform_rate_outlier_max,
        )
        return None

    # Fetch existing record
    result = await session.execute(
        select(PlatformRate).where(PlatformRate.platform == platform)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # --- EMA decay ---
        sample_count = existing.sample_count
        old_avg = existing.avg_rate
        alpha = min(settings.platform_rate_ema_alpha_max, 1.0 / (sample_count + 1))
        existing.avg_rate = (1 - alpha) * old_avg + alpha * rate
        existing.sample_count = sample_count + 1

        # --- Majority vote for common_type ---
        type_counts = dict(existing.type_counts or {})
        if rate_type:
            type_counts[rate_type] = type_counts.get(rate_type, 0) + 1
        existing.type_counts = type_counts

        # Determine majority type
        if type_counts:
            majority_type = max(type_counts, key=type_counts.get)
            existing.common_type = majority_type
        else:
            existing.common_type = None
    else:
        existing = PlatformRate(
            platform=platform,
            avg_rate=rate,
            common_type=rate_type,
            sample_count=1,
            confidence=0.0,
            type_counts={rate_type: 1} if rate_type else {},
        )
        session.add(existing)

    # Update confidence
    existing.confidence = min(1.0, existing.sample_count / settings.platform_rate_confidence_divisor)

    await session.commit()
    await session.refresh(existing)
    return existing


async def get_platform_rate(
    session: AsyncSession, platform: str
) -> PlatformRate | None:
    """Get a single platform rate by name."""
    result = await session.execute(
        select(PlatformRate).where(PlatformRate.platform == platform)
    )
    return result.scalar_one_or_none()


async def get_all_platform_rates(
    session: AsyncSession,
) -> list[PlatformRate]:
    """Get all platform rates."""
    result = await session.execute(select(PlatformRate))
    return list(result.scalars().all())


async def reset_platform_rate(
    session: AsyncSession, platform: str
) -> bool:
    """Reset all stats for a platform to zero (admin use).

    Returns True if a record existed and was deleted, False otherwise.
    """
    result = await session.execute(
        select(PlatformRate).where(PlatformRate.platform == platform)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        return False
    await session.delete(existing)
    await session.commit()
    logger.info("Platform rate reset for platform=%s", platform)
    return True
