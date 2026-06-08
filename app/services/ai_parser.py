import json
import logging
from datetime import date
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Anda adalah asisten yang mengekstrak informasi tagihan keuangan dari teks OCR Indonesia.
Ekstrak data berikut sebagai JSON:
- platform (string): nama platform/penyedia pinjaman. Cari merek seperti Akulaku, Kredivo, Shopee PayLater, Dana, GoPay Later, SPayLater, Home Credit, FIF, Adira, Kredit Pintar, easycash, dll. Jika tidak ditemukan, perhatikan konteks (misal "Rincian Pinjaman" dengan format tertentu bisa menunjukkan platform tertentu), atau gunakan "Tidak Diketahui".
- amount (number): jumlah tagihan YANG HARUS DIBAYAR SEKARANG. Prioritas: nominal cicilan bulanan saat ini (contoh: "3/3, Rp403.254" → 403254). Jangan ambil total Jumlah Pembayaran atau breakdown biaya. Jika ada beberapa angka, pilih yang paling relevan sebagai nominal utang aktif.
- due_date (string): tanggal jatuh tempo dalam format YYYY-MM-DD.
- installment_current (number atau null): cicilan ke-berapa (angka sebelum garis miring, contoh "3/3" → 3).
- installment_total (number atau null): total cicilan (angka setelah garis miring, contoh "3/3" → 3).
- category (string atau null): kategori pinjaman: "pinjol" (pinjaman online), "paylater", "kredit" (kredit bank/leasing), "gadai".
- notes (string atau null): catatan tambahan relevan.

Aturan penting:
- Angka dalam format Indonesia: "Rp1.000.000" = 1000000 (titik adalah pemisah ribuan). Hapus semua titik sebelum konversi ke number.
- Jangan pernah mengambil "Jumlah Pembayaran" atau total tagihan sebagai amount. Ambil nominal cicilan per bulan.
- Hanya kembalikan JSON valid, tanpa teks lain.
- Jika ragu, gunakan null."""


def _clean_parsed(parsed: dict[str, Any]) -> dict[str, Any]:
    import re
    today = date.today()

    platform = parsed.get("platform")
    if not platform or not isinstance(platform, str) or platform in ("Tidak Diketahui", "Unknown", ""):
        platform = None

    amount = parsed.get("amount")
    if isinstance(amount, str):
        amount = re.sub(r"[^0-9,]", "", amount)
        amount = amount.replace(",", ".")
        try:
            amount = int(float(amount))
        except (ValueError, TypeError):
            amount = None
    elif isinstance(amount, (int, float)):
        amount = int(amount)
    else:
        amount = None
    if amount is not None and amount <= 0:
        amount = None

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


_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_keepalive_connections=5))
    return _http_client


async def parse_debt_from_text(raw_text: str) -> dict[str, Any]:
    if not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY not configured")

    client = _get_client()
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
