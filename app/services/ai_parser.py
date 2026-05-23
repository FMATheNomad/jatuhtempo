import json
import logging
from datetime import date
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


def _clean_parsed(parsed: dict[str, Any]) -> dict[str, Any]:
    import re
    today = date.today()

    platform = parsed.get("platform")
    if not platform or not isinstance(platform, str):
        platform = "Tagihan"

    amount = parsed.get("amount")
    if not amount or not isinstance(amount, (int, float)):
        amount = 0
    amount = int(amount)

    raw_due = parsed.get("due_date")
    due_date = None
    if raw_due and isinstance(raw_due, str):
        try:
            due_date = date.fromisoformat(raw_due)
        except (ValueError, TypeError):
            pass
    if due_date is None:
        due_date = today

    return {
        "platform": platform,
        "amount": amount,
        "due_date": str(due_date),
        "installment_current": parsed.get("installment_current"),
        "installment_total": parsed.get("installment_total"),
        "category": parsed.get("category"),
        "notes": parsed.get("notes"),
    }


async def parse_debt_from_text(raw_text: str) -> dict[str, Any]:
    if not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY not configured")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.deepseek_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.deepseek_model,
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
        parsed = json.loads(content.strip())
        return _clean_parsed(parsed)
