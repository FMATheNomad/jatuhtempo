import re
import logging
from collections import defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.platforms import PLATFORMS

logger = logging.getLogger(__name__)

SEED_SIGNATURES: list[dict[str, Any]] = [
    # Akulaku
    {"platform": "Akulaku", "keyword": "rincian pinjaman", "weight": 5},
    {"platform": "Akulaku", "keyword": "biaya proteksi pinjaman", "weight": 3},
    {"platform": "Akulaku", "keyword": "no. pinjaman", "weight": 2},
    {"platform": "Akulaku", "keyword": "akulaku", "weight": 8},
    # Kredivo
    {"platform": "Kredivo", "keyword": "tagihan kredivo", "weight": 8},
    {"platform": "Kredivo", "keyword": "kredivo", "weight": 7},
    {"platform": "Kredivo", "keyword": "total pembayaran", "weight": 2},
    {"platform": "Kredivo", "keyword": "rincian pembayaran", "weight": 3},
    # Shopee PayLater
    {"platform": "Shopee PayLater", "keyword": "spaylater", "weight": 8},
    {"platform": "Shopee PayLater", "keyword": "shopee paylater", "weight": 8},
    {"platform": "Shopee PayLater", "keyword": "tagihan shopee", "weight": 5},
    {"platform": "Shopee PayLater", "keyword": "cicilan shopee", "weight": 4},
    # GoPay Later
    {"platform": "GoPay Later", "keyword": "gopay later", "weight": 8},
    {"platform": "GoPay Later", "keyword": "goplay later", "weight": 7},
    {"platform": "GoPay Later", "keyword": "total tagihan", "weight": 2},
    # Home Credit
    {"platform": "Home Credit", "keyword": "home credit", "weight": 8},
    {"platform": "Home Credit", "keyword": "nomor kontrak", "weight": 3},
    {"platform": "Home Credit", "keyword": "angsuran ke-", "weight": 3},
    # FIF
    {"platform": "FIF", "keyword": "fifgroup", "weight": 8},
    {"platform": "FIF", "keyword": "federal international finance", "weight": 7},
    {"platform": "FIF", "keyword": "pt fif", "weight": 6},
    # Adira
    {"platform": "Adira", "keyword": "adira", "weight": 7},
    {"platform": "Adira", "keyword": "adira finance", "weight": 8},
    # Kredit Pintar
    {"platform": "Kredit Pintar", "keyword": "kredit pintar", "weight": 8},
    {"platform": "Kredit Pintar", "keyword": "kreditpintar", "weight": 7},
    # EasyCash
    {"platform": "EasyCash", "keyword": "easycash", "weight": 8},
    {"platform": "EasyCash", "keyword": "easy cash", "weight": 7},
    # BCA
    {"platform": "BCA", "keyword": "bca", "weight": 5},
    {"platform": "BCA", "keyword": "bank bca", "weight": 7},
    {"platform": "BCA", "keyword": "kartu kredit bca", "weight": 6},
    # Mandiri
    {"platform": "Mandiri", "keyword": "bank mandiri", "weight": 7},
    {"platform": "Mandiri", "keyword": "tagihan mandiri", "weight": 6},
    {"platform": "Mandiri", "keyword": "kartu kredit mandiri", "weight": 5},
]


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
    from app.models.platform_signature import PlatformSignature

    if not text:
        return None

    text_lower = text.lower()
    result = await session.execute(select(PlatformSignature))
    signatures = result.scalars().all()

    scores: dict[str, int] = defaultdict(int)
    for sig in signatures:
        if sig.keyword in text_lower:
            scores[sig.platform] += sig.weight

    if not scores:
        return None

    sorted_platforms = sorted(scores.items(), key=lambda x: -x[1])
    top_platform, top_score = sorted_platforms[0]

    if len(sorted_platforms) > 1:
        second_score = sorted_platforms[1][1]
        if top_score - second_score < 3:
            return None

    return top_platform


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
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
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
