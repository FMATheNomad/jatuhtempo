import json
import logging
import random
from datetime import date, datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BLOG_PILLARS = [
    {
        "pillar": "edukasi",
        "title": "Apa Itu Snowball Method dan Kenapa Efektif buat Lunasi Utang?",
        "prompt": "Buat artikel blog edukatif tentang snowball method. Jelaskan konsepnya dengan analogi sederhana, kenapa metode ini efektif secara psikologis, dan contoh konkret dengan angka. Gaya: Tim Riset JatuhTempo — informatif, berbasis data, tapi tetap ringan dibaca. Akhiri dengan CTA untuk coba fitur strategi di JatuhTempo.",
    },
    {
        "pillar": "edukasi",
        "title": "Cicilan Tetap vs Cicilan Menurun: Mana yang Lebih Baik?",
        "prompt": "Buat artikel blog yang menjelaskan perbedaan cicilan tetap (flat) dan cicilan menurun (efektif). Berikan contoh perhitungan sederhana. Jelaskan kapan masing-masing lebih menguntungkan. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA untuk tracking cicilan pakai JatuhTempo.",
    },
    {
        "pillar": "data",
        "title": "Rata-Rata Bunga Pinjol di Indonesia",
        "prompt": "Buat artikel blog informatif tentang rata-rata bunga pinjaman online di Indonesia. Gunakan data berikut sebagai referensi. Jelaskan pentingnya mengetahui bunga pasar sebelum mengambil pinjaman. Gaya: Tim Riset JatuhTempo — data-driven, faktual. Akhiri dengan CTA cek bunga pinjaman kamu di JatuhTempo.",
    },
    {
        "pillar": "data",
        "title": "Perbandingan Bunga Kredivo, Akulaku, dan Shopee PayLater",
        "prompt": "Buat artikel blog yang membandingkan bunga Kredivo, Akulaku, dan Shopee PayLater berdasarkan data yang tersedia. Help pembaca memahami mana yang paling murah dan kapan harus pakai yang mana. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking semua utang di satu tempat pake JatuhTempo.",
    },
    {
        "pillar": "psikologi",
        "title": "Kenapa Banyak Orang Terjebak Utang PayLater?",
        "prompt": "Buat artikel blog tentang psikologi di balik utang payLater: efek kemudahan, underestimasi bunga, dan normalisasi cicilan. Gaya: Tim Riset JatuhTempo — naratif, insightful. Akhiri dengan CTA untuk evaluasi total utang pakai JatuhTempo.",
    },
    {
        "pillar": "psikologi",
        "title": "Stres Akibat Utang: Kapan Harus Mencari Bantuan?",
        "prompt": "Buat artikel blog tentang stres finansial yang disebabkan utang. Tanda-tanda, dampak psikologis, dan kapan harus mencari bantuan profesional. Gaya: Tim Riset JatuhTempo — empati, informatif. Akhiri dengan CTA untuk mulai tracking utang sebagai langkah pertama mengurangi stres.",
    },
    {
        "pillar": "produk",
        "title": "3 Fitur JatuhTempo yang Bikin Hidup Lebih Tenang",
        "prompt": "Buat artikel blog tentang 3 fitur utama JatuhTempo: scan tagihan AI, reminder Telegram otomatis, dan strategi snowball. Jelaskan benefit masing-masing dengan cerita singkat. Gaya: Tim Riset JatuhTempo — hangat, personal. Akhiri dengan CTA cobain JatuhTempo gratis.",
    },
    {
        "pillar": "produk",
        "title": "Cara Scan Tagihan dengan AI di JatuhTempo",
        "prompt": "Buat artikel tutorial cara menggunakan fitur scan tagihan di JatuhTempo. Step-by-step: buka bot, kirim foto, konfirmasi, selesai. Bahasa ringan. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA cobain sekarang.",
    },
    {
        "pillar": "edukasi",
        "title": "Tips Prioritas Utang: Mana yang Harus Dibayar Duluan?",
        "prompt": "Buat artikel blog yang mengedukasi pembaca cara memprioritaskan utang: bunga tertinggi duluan vs jumlah terkecil duluan. Beri contoh skenario. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA untuk lihat strategi personal di JatuhTempo.",
    },
    {
        "pillar": "data",
        "title": "Berapa Idealnya Rasio Utang terhadap Penghasilan?",
        "prompt": "Buat artikel blog edukatif tentang DTI ratio (Debt-to-Income). Jelaskan angka ideal, cara hitung, dan apa yang harus dilakukan jika terlalu tinggi. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking utang + penghasilan pakai JatuhTempo.",
    },
]


async def generate_content() -> dict | None:
    if not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY not set, skipping content generation")
        return None

    prompt_data = random.choice(_BLOG_PILLARS)

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
                        {"role": "system", "content": (
                            "Kamu adalah Tim Riset JatuhTempo — penulis konten keuangan yang informatif, "
                            "berbasis data, dan tepercaya. Gaya penulisan: hangat, jelas, tidak menggurui. "
                            "Target pembaca: orang Indonesia 20-35 tahun yang punya utang konsumtif "
                            "(paylater, pinjol, kartu kredit).\n\n"
                            "Aturan:\n"
                            "1. Jangan mengarang data atau angka tanpa sumber. Jika tidak yakin, gunakan istilah umum.\n"
                            "2. Panjang artikel: 300-500 kata. Tidak perlu judul (saya yang handle).\n"
                            "3. Bahasa Indonesia yang baik, santai, tidak kaku.\n"
                            "4. Akhiri dengan ajakan (CTA) yang relevan tapi tidak maksa.\n"
                            "5. Jangan promotif berlebihan. Konten harus berdiri sendiri sebagai artikel informatif."
                        )},
                        {"role": "user", "content": prompt_data["prompt"]},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            result = {
                "pillar": prompt_data["pillar"],
                "title": prompt_data["title"],
                "content": content,
                "generated_at": datetime.now().isoformat(),
                "source": "Tim Riset JatuhTempo",
                "posted": False,
            }

            _save_to_file(result)
            logger.info("Blog post generated: %s [%s]", prompt_data["title"], prompt_data["pillar"])
            return result

    except Exception as e:
        logger.exception("Failed to generate content: %s", e)
        return None


def _save_to_file(content: dict) -> None:
    import os
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "generated_content.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(content) + "\n")
    logger.info("Content saved to %s", log_file)
