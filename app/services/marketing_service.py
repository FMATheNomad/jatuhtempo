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
        "pillar": "edukasi",
        "title": "Tips Prioritas Utang: Mana yang Harus Dibayar Duluan?",
        "prompt": "Buat artikel blog yang mengedukasi pembaca cara memprioritaskan utang: bunga tertinggi duluan vs jumlah terkecil duluan. Beri contoh skenario. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA untuk lihat strategi personal di JatuhTempo.",
    },
    {
        "pillar": "data",
        "title": "Rata-Rata Bunga Pinjol di Indonesia",
        "prompt": "Buat artikel blog informatif tentang rata-rata bunga pinjaman online di Indonesia. Jelaskan pentingnya mengetahui bunga pasar sebelum mengambil pinjaman. Gaya: Tim Riset JatuhTempo — data-driven, faktual. Akhiri dengan CTA cek bunga pinjaman kamu di JatuhTempo.",
    },
    {
        "pillar": "data",
        "title": "Perbandingan Bunga Kredivo, Akulaku, dan Shopee PayLater",
        "prompt": "Buat artikel blog yang membandingkan bunga Kredivo, Akulaku, dan Shopee PayLater. Help pembaca memahami mana yang paling murah dan kapan harus pakai yang mana. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking semua utang di satu tempat pake JatuhTempo.",
    },
    {
        "pillar": "data",
        "title": "Dampak Suku Bunga BI Terhadap Utang Konsumtif",
        "prompt": "Buat artikel yang menjelaskan hubungan antara suku bunga acuan Bank Indonesia (BI Rate) dengan bunga pinjaman konsumtif di Indonesia. Bagaimana kenaikan BI Rate mempengaruhi cicilan Kredivo, pinjol, dan kartu kredit. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking utang biar tetap aware dengan perubahan bunga.",
    },
    {
        "pillar": "ekonomi",
        "title": "Dampak Inflasi Terhadap Daya Beli Masyarakat Indonesia 2026",
        "prompt": "Buat artikel tentang inflasi di Indonesia tahun 2026: penyebab, dampak ke daya beli, dan strategi bertahan. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA untuk evaluasi pengeluaran dan utang.",
    },
    {
        "pillar": "ekonomi",
        "title": "Kenaikan PPN 12%: Dampaknya buat Keuangan Sehari-hari",
        "prompt": "Bahas kenaikan PPN menjadi 12% di Indonesia: sektor mana yang terpengaruh, dampak ke pengeluaran rumah tangga, dan tips adaptasi. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking pengeluaran dan utang.",
    },
    {
        "pillar": "ekonomi",
        "title": "Kebijakan OJK 2026 yang Perlu Kamu Tahu sebagai Peminjam",
        "prompt": "Bahas kebijakan OJK terbaru tahun 2026 yang relevan untuk peminjam: aturan pinjol, batas bunga, perlindungan konsumen. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking status utang sesuai regulasi.",
    },
    {
        "pillar": "psikologi",
        "title": "Kenapa Banyak Orang Terjebak Utang PayLater?",
        "prompt": "Buat artikel tentang psikologi di balik utang paylater: efek kemudahan, underestimasi bunga, normalisasi cicilan. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA evaluasi total utang.",
    },
    {
        "pillar": "psikologi",
        "title": "Financial Anxiety: Cara Mengatasi Stres Akibat Masalah Uang",
        "prompt": "Buat artikel tentang financial anxiety: gejala, penyebab, dan langkah-langkah praktis mengatasinya. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking sebagai langkah awal mengurangi stres.",
    },
    {
        "pillar": "teknologi",
        "title": "AI untuk Keuangan Pribadi: Antara Kemudahan dan Risiko",
        "prompt": "Bahas perkembangan AI di aplikasi keuangan pribadi: apa yang bisa dilakukan AI, risiko privasi, dan masa depan personal finance. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA yang relevan.",
    },
    {
        "pillar": "teknologi",
        "title": "Keamanan Data Finansial di Era Digital",
        "prompt": "Buat artikel tentang pentingnya keamanan data finansial: tips melindungi data, enkripsi, dan praktik aman. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA yang relevan.",
    },
    {
        "pillar": "gaya-hidup",
        "title": "Mindful Spending: Cara Belanja Tanpa Bersalah",
        "prompt": "Buat artikel tentang konsep mindful spending: bagaimana membedakan kebutuhan vs keinginan, tips belanja bijak, dan tetap menikmati hidup tanpa over budget. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking pengeluaran.",
    },
    {
        "pillar": "gaya-hidup",
        "title": "Side Hustle untuk Bayar Utang Lebih Cepat",
        "prompt": "Bahas berbagai side hustle yang cocok untuk orang Indonesia: freelance, reseller, content creator. Fokus pada yang modal kecil. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA alokasi penghasilan tambahan untuk lunasi utang.",
    },
    {
        "pillar": "gaya-hidup",
        "title": "Frugal Living vs Quality of Life: Mencari Titik Tengah",
        "prompt": "Bahas konsep frugal living yang realistis untuk anak muda Indonesia: tips hemat tanpa bikin stres, investasi di quality of life yang penting. Gaya: Tim Riset JatuhTempo. Akhiri dengan CTA tracking utang dan pengeluaran.",
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
