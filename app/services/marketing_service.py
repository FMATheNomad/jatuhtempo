import json
import logging
import random
from datetime import date, datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_CONTENT_PROMPTS = [
    {
        "type": "thread",
        "title": "Berapa total utang lo?",
        "prompt": (
            "Buat thread pendek (3-5 kalimat) dalam Bahasa Indonesia casual tentang "
            "betapa mudahnya kehilangan track total utang ketika punya lebih dari 2 tagihan. "
            "Gaya bahasa santai kayak ngobrol sama temen. Akhiri dengan ajakan cek "
            "total utang pakai JatuhTempo (gratis). Jangan promosi berlebihan."
        ),
    },
    {
        "type": "tip",
        "title": "Snowball method buat pemula",
        "prompt": (
            "Buat thread singkat dalam Bahasa Indonesia yang explain snowball method "
            "(lunasi utang dari yang terkecil dulu) dengan analogi sederhana. "
            "Tambahkan contoh konkret. Gaya santai, edukatif. Akhiri dengan "
            "mention JatuhTempo sebagai tools untuk tracking."
        ),
    },
    {
        "type": "fact",
        "title": "Rata-rata bunga pinjol",
        "prompt": (
            "Buat postingan pendek dalam Bahasa Indonesia tentang fakta menarik "
            "seputar bunga pinjaman online. Gaya santai, informatif. "
            "Kasih perspektif baru. Akhiri dengan ajakan untuk lebih aware dengan "
            "tracking utang."
        ),
    },
    {
        "type": "motivation",
        "title": "Gue pernah ada di posisi lo",
        "prompt": (
            "Buat thread singkat dalam Bahasa Indonesia dari sudut pandang orang "
            "yang pernah punya banyak utang dan berhasil melunasinya. "
            "Gaya cerita personal, jujur, relatable. Pesan utama: lo gak sendirian. "
            "Akhiri dengan ajakan tracking utang."
        ),
    },
    {
        "type": "tip",
        "title": "Prioritasin utang yang mana dulu?",
        "prompt": (
            "Buat postingan edukatif dalam Bahasa Indonesia yang jelasin perbedaan "
            "snowball (dari terkecil) vs avalanche (bunga tertinggi). "
            "Beri contoh sederhana. Akhiri dengan rekomendasi personal. "
            "Santai, gak kaku."
        ),
    },
    {
        "type": "thread",
        "title": "3 tools gratis yang gue pake buat tracking utang",
        "prompt": (
            "Buat thread singkat dalam Bahasa Indonesia yang mention 2 tools umum "
            "(notes, spreadsheet) lalu mention JatuhTempo sebagai alternatif paling "
            "canggih (OCR, reminder Telegram). "
            "Bandingkan secara fair. Akhiri dengan ajakan cobain."
        ),
    },
]


async def generate_content() -> dict | None:
    """Generate marketing content using DeepSeek API."""
    if not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY not set, skipping content generation")
        return None

    prompt_data = random.choice(_CONTENT_PROMPTS)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.deepseek_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.deepseek_model,
                    "messages": [
                        {"role": "system", "content": "Kamu adalah social media manager untuk JatuhTempo, aplikasi manajemen utang Indonesia. Gaya bahasa: santai, casual, kayak ngobrol sama temen. Maksimal 300 karakter per postingan. Gunakan emoji secukupnya. Jangan lebay."},
                        {"role": "user", "content": prompt_data["prompt"]},
                    ],
                    "temperature": 0.8,
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            result = {
                "type": prompt_data["type"],
                "title": prompt_data["title"],
                "content": content,
                "generated_at": datetime.now().isoformat(),
                "platform": "threads",
                "posted": False,
            }

            _save_to_file(result)
            logger.info("Content generated: %s", prompt_data["title"])
            return result

    except Exception as e:
        logger.exception("Failed to generate content: %s", e)
        return None


def _save_to_file(content: dict) -> None:
    """Append generated content to a local JSONL file for review."""
    import os
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "generated_content.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(content) + "\n")
    logger.info("Content saved to %s", log_file)
