import json
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Anda adalah asisten yang mengekstrak informasi tagihan keuangan dari teks OCR Indonesia.
Ekstrak data berikut sebagai JSON:
- platform (string): nama platform pinjaman/paylater (contoh: Akulaku, Shopee PayLater, Kredivo, dll)
- amount (number): jumlah tagihan dalam Rupiah (angka saja, tanpa Rp atau titik)
- due_date (string): tanggal jatuh tempo dalam format YYYY-MM-DD
- installment_current (number atau null): cicilan ke-berapa (jika ada)
- installment_total (number atau null): total cicilan (jika ada)
- category (string atau null): kategori (contoh: "pinjol", "paylater", "gadai", "kredit")
- notes (string atau null): catatan tambahan

Hanya kembalikan JSON, tanpa teks lain.
Jika ragu, gunakan null untuk nilai yang tidak diketahui."""


async def parse_debt_from_text(raw_text: str) -> dict[str, Any]:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not configured")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/FMATheNomad/jatuhtempo",
                "X-Title": "JatuhTempo",
            },
            json={
                "model": settings.openrouter_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": raw_text},
                ],
                "temperature": 0.1,
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content.strip())
