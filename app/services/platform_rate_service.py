import logging
import math
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.platform_rate import PlatformRate

logger = logging.getLogger(__name__)


async def update_platform_rate(
    session: AsyncSession, platform: str, rate: float, rate_type: str | None
) -> PlatformRate | None:
    """Upsert platform rate with EMA decay, time decay, variance, and adaptive outlier detection.

    New in v2:
    - Time-based decay: older data gets weighted less
    - Running variance (Welford's online algorithm): for adaptive confidence
    - Per-platform adaptive bounds: learns normal range from data
    - Rejected outliers logged for monitoring
    """
    result = await session.execute(
        select(PlatformRate).where(PlatformRate.platform == platform)
    )
    existing = result.scalar_one_or_none()

    outlier_reason = _is_outlier(existing, rate)
    if outlier_reason:
        logger.warning(
            "Outlier rejected for platform=%s: rate=%.4f reason=%s "
            "(sample_count=%s, min=%.2f, max=%.2f)",
            platform, rate, outlier_reason,
            existing.sample_count if existing else 0,
            existing.min_rate if existing and existing.min_rate is not None else 0,
            existing.max_rate if existing and existing.max_rate is not None else 0,
        )
        if existing:
            existing.outlier_count = (existing.outlier_count or 0) + 1
            await session.commit()
        return None

    now = datetime.now(timezone.utc)

    if existing:
        sample_count = existing.sample_count
        old_avg = existing.avg_rate
        old_std = existing.rate_std or 0.0
        old_min = existing.min_rate
        old_max = existing.max_rate

        months_since_update = 0
        if existing.last_rate_update:
            try:
                delta = now - existing.last_rate_update
                months_since_update = delta.days / 30.0
            except TypeError:
                months_since_update = 0

        time_boost = 1.0 + min(
            settings.platform_rate_time_decay_max - 1.0,
            months_since_update * 0.1,
        )
        alpha = min(settings.platform_rate_ema_alpha_max, 1.0 / (sample_count + 1))
        alpha = min(0.5, alpha * time_boost)

        new_avg = (1 - alpha) * old_avg + alpha * rate

        new_std = _update_std_welford(old_std, old_avg, rate, sample_count)

        existing.avg_rate = new_avg
        existing.rate_std = round(new_std, 6)
        existing.sample_count = sample_count + 1
        existing.min_rate = min(old_min, rate) if old_min is not None else rate
        existing.max_rate = max(old_max, rate) if old_max is not None else rate
        existing.last_rate_update = now

        if rate_type:
            type_counts = dict(existing.type_counts or {})
            type_counts[rate_type] = type_counts.get(rate_type, 0) + 1
            existing.type_counts = type_counts
            majority_type = max(type_counts, key=type_counts.get)
            existing.common_type = majority_type
    else:
        existing = PlatformRate(
            platform=platform,
            avg_rate=rate,
            common_type=rate_type,
            sample_count=1,
            confidence=0.0,
            type_counts={rate_type: 1} if rate_type else {},
            rate_std=0.0,
            min_rate=rate,
            max_rate=rate,
            last_rate_update=now,
            outlier_count=0,
        )
        session.add(existing)

    existing.confidence = _compute_confidence(existing)

    await session.commit()
    await session.refresh(existing)
    return existing


def _is_outlier(existing: PlatformRate | None, rate: float) -> str | None:
    """Adaptive outlier detection using per-platform bounds when available, global fallback."""
    if rate < settings.platform_rate_outlier_min:
        return f"below_global_min_{settings.platform_rate_outlier_min}"
    if rate > settings.platform_rate_outlier_max:
        return f"above_global_max_{settings.platform_rate_outlier_max}"

    if existing and existing.sample_count >= 10 and existing.rate_std and existing.min_rate is not None and existing.max_rate is not None:
        margin = max(existing.rate_std * 3, (existing.max_rate - existing.min_rate) * 0.5)
        lower = max(settings.platform_rate_outlier_min, existing.avg_rate - margin)
        upper = min(settings.platform_rate_outlier_max, existing.avg_rate + margin)
        if rate < lower:
            return f"below_adaptive_bound_{lower:.2f}"
        if rate > upper:
            return f"above_adaptive_bound_{upper:.2f}"

    return None


def _update_std_welford(old_std: float, old_mean: float, new_value: float, n: int) -> float:
    """Welford's online algorithm for running variance."""
    if n == 0:
        return 0.0
    delta = new_value - old_mean
    new_mean = old_mean + delta / (n + 1)
    delta2 = new_value - new_mean
    if n == 1:
        return abs(delta)
    new_var = ((n - 1) * (old_std ** 2) + delta * delta2) / n
    return math.sqrt(new_var) if new_var > 0 else 0.0


def _compute_confidence(rate: PlatformRate) -> float:
    """Confidence = sample_count/20 * stability_factor.

    stability_factor = 1 / (1 + std/mean) when mean > 0 and std exists.
    High variance → lower confidence, even with many samples.
    """
    base = min(1.0, rate.sample_count / settings.platform_rate_confidence_divisor)
    if rate.avg_rate > 0 and rate.rate_std and rate.rate_std > 0:
        cv = rate.rate_std / rate.avg_rate
        stability = 1.0 / (1.0 + cv)
        return round(min(1.0, base * (0.3 + 0.7 * stability)), 6)
    return round(base, 6)


async def get_platform_rate(
    session: AsyncSession, platform: str
) -> PlatformRate | None:
    result = await session.execute(
        select(PlatformRate).where(PlatformRate.platform == platform)
    )
    return result.scalar_one_or_none()


async def get_all_platform_rates(
    session: AsyncSession,
) -> list[PlatformRate]:
    result = await session.execute(select(PlatformRate))
    return list(result.scalars().all())


async def reset_platform_rate(
    session: AsyncSession, platform: str
) -> bool:
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
