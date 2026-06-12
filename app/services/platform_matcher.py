import re
import logging
from collections import defaultdict
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.platforms import PLATFORMS

logger = logging.getLogger(__name__)

SEED_SIGNATURES: list[dict[str, Any]] = [
    {"platform": "Akulaku", "keyword": "rincian pinjaman", "weight": 5},
    {"platform": "Akulaku", "keyword": "biaya proteksi pinjaman", "weight": 3},
    {"platform": "Akulaku", "keyword": "no. pinjaman", "weight": 2},
    {"platform": "Akulaku", "keyword": "akulaku", "weight": 8},
    {"platform": "Kredivo", "keyword": "tagihan kredivo", "weight": 8},
    {"platform": "Kredivo", "keyword": "kredivo", "weight": 7},
    {"platform": "Kredivo", "keyword": "total pembayaran", "weight": 2},
    {"platform": "Kredivo", "keyword": "rincian pembayaran", "weight": 3},
    {"platform": "Shopee PayLater", "keyword": "spaylater", "weight": 8},
    {"platform": "Shopee PayLater", "keyword": "shopee paylater", "weight": 8},
    {"platform": "Shopee PayLater", "keyword": "tagihan shopee", "weight": 5},
    {"platform": "Shopee PayLater", "keyword": "cicilan shopee", "weight": 4},
    {"platform": "GoPay Later", "keyword": "gopay later", "weight": 8},
    {"platform": "GoPay Later", "keyword": "goplay later", "weight": 7},
    {"platform": "GoPay Later", "keyword": "total tagihan", "weight": 2},
    {"platform": "Home Credit", "keyword": "home credit", "weight": 8},
    {"platform": "Home Credit", "keyword": "nomor kontrak", "weight": 3},
    {"platform": "Home Credit", "keyword": "angsuran ke", "weight": 3},
    {"platform": "FIF", "keyword": "fifgroup", "weight": 8},
    {"platform": "FIF", "keyword": "federal international finance", "weight": 7},
    {"platform": "FIF", "keyword": "pt fif", "weight": 6},
    {"platform": "Adira", "keyword": "adira", "weight": 7},
    {"platform": "Adira", "keyword": "adira finance", "weight": 8},
    {"platform": "Kredit Pintar", "keyword": "kredit pintar", "weight": 8},
    {"platform": "Kredit Pintar", "keyword": "kreditpintar", "weight": 7},
    {"platform": "EasyCash", "keyword": "easycash", "weight": 8},
    {"platform": "EasyCash", "keyword": "easy cash", "weight": 7},
    {"platform": "BCA", "keyword": "bca", "weight": 5},
    {"platform": "BCA", "keyword": "bank bca", "weight": 7},
    {"platform": "BCA", "keyword": "kartu kredit bca", "weight": 6},
    {"platform": "Mandiri", "keyword": "bank mandiri", "weight": 7},
    {"platform": "Mandiri", "keyword": "tagihan mandiri", "weight": 6},
    {"platform": "Mandiri", "keyword": "kartu kredit mandiri", "weight": 5},
]

_PLATFORM_ALIASES: dict[str, str] = {
    "bca": "BCA",
    "mandiri": "Mandiri",
    "bni": "BNI",
    "bri": "BRI",
    "danamon": "Danamon",
    "permata": "Permata",
    "maybank": "Maybank",
    "cimb": "CIMB Niaga",
    "cimb niaga": "CIMB Niaga",
    "akulaku": "Akulaku",
    "kredivo": "Kredivo",
    "shopee": "Shopee PayLater",
    "spaylater": "Shopee PayLater",
    "gopay": "GoPay Later",
    "gopay later": "GoPay Later",
    "home credit": "Home Credit",
    "fif": "FIF",
    "adira": "Adira",
    "kredit pintar": "Kredit Pintar",
    "kreditpintar": "Kredit Pintar",
    "easycash": "EasyCash",
    "easy cash": "EasyCash",
    "dana": "Dana",
}


async def seed_signatures(session: AsyncSession):
    from app.models.platform_signature import PlatformSignature
    result = await session.execute(select(PlatformSignature).limit(1))
    if result.scalar_one_or_none():
        return
    for sig in SEED_SIGNATURES:
        session.add(PlatformSignature(**sig))
    await session.commit()
    logger.info(f"Seeded {len(SEED_SIGNATURES)} platform signatures")


async def match_platform(text: str, session: AsyncSession) -> str | None:
    result, _, _ = await _score_platforms(text, session)
    return result


async def match_platform_with_confidence(
    text: str, session: AsyncSession
) -> tuple[str | None, float, dict[str, int]]:
    return await _score_platforms(text, session)


async def _score_platforms(
    text: str, session: AsyncSession
) -> tuple[str | None, float, dict[str, int]]:
    if not text:
        return None, 0.0, {}

    from app.models.platform_signature import PlatformSignature

    text_lower = text.lower()
    result = await session.execute(select(PlatformSignature))
    signatures = result.scalars().all()

    scores: dict[str, int] = defaultdict(int)
    for sig in signatures:
        if sig.keyword in text_lower:
            scores[sig.platform] += sig.weight

    if not scores:
        alias = _check_aliases(text_lower)
        if alias:
            return alias, 0.5, {}
        return None, 0.0, {}

    sorted_pairs = sorted(scores.items(), key=lambda x: -x[1])
    top_platform, top_score = sorted_pairs[0]

    total_score = sum(v for _, v in sorted_pairs)

    if len(sorted_pairs) > 1:
        second_score = sorted_pairs[1][1]
        gap = top_score - second_score
        min_gap = max(
            settings.platform_matcher_tiebreaker_min,
            int(top_score * settings.platform_matcher_tiebreaker_ratio),
        )
        if gap < min_gap:
            return None, 0.0, dict(sorted_pairs)

    if total_score > 0:
        confidence = min(1.0, top_score / max(total_score * 0.6, 1))
    else:
        confidence = 0.0

    return top_platform, round(confidence, 4), dict(sorted_pairs)


def _check_aliases(text_lower: str) -> str | None:
    """Fallback alias check for short/partial texts where keyword matching fails."""
    for alias, platform in _PLATFORM_ALIASES.items():
        if alias in text_lower:
            return platform
    return None


async def reinforce_match(
    session: AsyncSession,
    raw_text: str,
    confirmed_platform: str,
) -> None:
    """Positive reinforcement: boost weights of keywords that led to a correct match.

    Called when user confirms a debt after our platform suggestion was correct.
    """
    from app.models.platform_signature import PlatformSignature

    if not raw_text or not confirmed_platform:
        return

    text_lower = raw_text.lower()
    result = await session.execute(
        select(PlatformSignature).where(PlatformSignature.platform == confirmed_platform)
    )
    matched = False
    for sig in result.scalars().all():
        if sig.keyword in text_lower:
            sig.weight = sig.weight + settings.platform_matcher_confidence_reinforce_weight
            matched = True

    if not matched:
        words = _extract_keywords(raw_text)
        for w in words:
            if w in confirmed_platform.lower() or len(w) > 4:
                existing = await session.execute(
                    select(PlatformSignature).where(
                        PlatformSignature.keyword == w,
                        PlatformSignature.platform == confirmed_platform,
                    )
                )
                if not existing.scalar_one_or_none():
                    session.add(PlatformSignature(
                        platform=confirmed_platform,
                        keyword=w,
                        weight=3,
                        source="implicit",
                    ))
                    matched = True
                    break

    if matched:
        await session.commit()


async def penalize_mistake(
    session: AsyncSession,
    raw_text: str,
    wrong_platform: str,
    correct_platform: str,
) -> None:
    """Negative feedback: reduce weights of wrongly-matched keywords.

    Called when a user edits/overrides a platform we suggested.
    """
    from app.models.platform_signature import PlatformSignature

    if not raw_text or not correct_platform:
        return

    text_lower = raw_text.lower()

    wrong_result = await session.execute(
        select(PlatformSignature).where(PlatformSignature.platform == wrong_platform)
    )
    for sig in wrong_result.scalars().all():
        if sig.keyword in text_lower:
            sig.weight = max(0.5, sig.weight - 1.0)

    words = _extract_keywords(raw_text)
    for w in words:
        if w in correct_platform.lower().split() or len(w) > 4:
            existing = await session.execute(
                select(PlatformSignature).where(
                    PlatformSignature.keyword == w,
                    PlatformSignature.platform == correct_platform,
                )
            )
            if not existing.scalar_one_or_none():
                session.add(PlatformSignature(
                    platform=correct_platform,
                    keyword=w,
                    weight=5,
                    source="correction",
                ))

    await session.commit()


async def learn_from_correction(
    session: AsyncSession,
    raw_text: str,
    correct_platform: str,
    incorrect_platform: str | None = None,
):
    from app.models.platform_signature import PlatformSignature

    if not raw_text:
        return

    text_lower = raw_text.lower()
    words = _extract_keywords(raw_text)
    word_scores: dict[str, int] = defaultdict(int)

    for w in words:
        if incorrect_platform and w in incorrect_platform.lower():
            word_scores[w] = word_scores.get(w, 0) - 5
        if w in correct_platform.lower().split():
            word_scores[w] = word_scores.get(w, 0) + 5

    for w, score in word_scores.items():
        if score > 0:
            existing = await session.execute(
                select(PlatformSignature).where(
                    PlatformSignature.keyword == w,
                    PlatformSignature.platform == correct_platform,
                )
            )
            if not existing.scalar_one_or_none():
                session.add(PlatformSignature(
                    platform=correct_platform,
                    keyword=w,
                    weight=score,
                    source="correction",
                ))

    existing_raw = await session.execute(
        select(PlatformSignature).where(
            PlatformSignature.keyword == text_lower[:100],
            PlatformSignature.platform == correct_platform,
        )
    )
    if not existing_raw.scalar_one_or_none():
        session.add(PlatformSignature(
            platform=correct_platform,
            keyword=text_lower[:200],
            weight=2,
            source="correction",
        ))

    await session.commit()


def _extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text, supporting Indonesian + alphanumeric."""
    text_lower = text.lower()
    min_len = settings.platform_matcher_min_keyword_length
    words = re.findall(rf'\b[\w]{{{min_len},}}\b', text_lower)
    stopwords = {
        "dan", "atau", "yang", "di", "ke", "dengan", "ini", "itu",
        "dan", "ada", "juga", "dari", "untuk", "pada", "akan",
        "telah", "sudah", "bisa", "dapat", "tidak", "akan",
    }
    return [w for w in words if w not in stopwords and not w.isdigit()]
