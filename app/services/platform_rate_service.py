import logging
from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform_rate import PlatformRate

logger = logging.getLogger(__name__)


async def update_platform_rate(
    session: AsyncSession, platform: str, rate: float, rate_type: str | None
) -> PlatformRate:
    """Upsert platform rate: recalculate avg_rate, increment sample_count, update confidence."""
    # Fetch existing record
    result = await session.execute(
        select(PlatformRate).where(PlatformRate.platform == platform)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Recalculate weighted average
        old_total = existing.avg_rate * existing.sample_count
        new_sample_count = existing.sample_count + 1
        existing.avg_rate = (old_total + rate) / new_sample_count
        existing.sample_count = new_sample_count

        # Track type frequency — we store the latest type for simplicity
        # but we need most common across all samples. We don't have a history
        # table, so we approximate: if common_type matches new type, keep it;
        # if different, set to None (uncertain) unless we have strong evidence.
        # A better approach: always update common_type to the most recent if
        # it's consistent, else None.
        if existing.common_type == rate_type:
            pass  # already matches
        elif existing.common_type is None:
            existing.common_type = rate_type
        else:
            # Conflicting types — set to None unless the new one dominates
            # We'll use a simple heuristic: if we only have 1-2 samples,
            # trust the new one; if we have many and they conflict, mark None.
            if existing.sample_count <= 3:
                existing.common_type = rate_type
            else:
                existing.common_type = None
    else:
        existing = PlatformRate(
            platform=platform,
            avg_rate=rate,
            common_type=rate_type,
            sample_count=1,
            confidence=0.0,
        )
        session.add(existing)

    # Update confidence: min(1.0, sample_count / 20)
    existing.confidence = min(1.0, existing.sample_count / 20)

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
