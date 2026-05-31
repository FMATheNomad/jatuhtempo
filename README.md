# 🧠 JatuhTempo — AI-Powered Debt Management Assistant

Asisten manajemen utang berbasis AI untuk pengguna Indonesia. Multi-platform — mulai dari Telegram bot hingga REST API.

Kirim screenshot tagihan, biarkan AI yang mengekstrak jumlah, platform, dan jatuh tempo. Atau catat manual. Dapatkan pengingat otomatis sebelum telat bayar.

---

## ✨ Fitur

### 📸 OCR + AI Parsing
- Upload screenshot tagihan → PaddleOCR baca teks → DeepSeek AI ekstrak data terstruktur
- Otomatis deteksi: platform (Akulaku, Kredivo, Shopee PayLater, dll), jumlah, tanggal jatuh tempo, cicilan

### 📝 Manual Entry
- Catat utang langsung via Telegram: `/add Akulaku 500000 2026-06-15`

### 🔔 Pengingat Otomatis
- H-7, H-3, H-1, hari-H, dan keterlambatan
- Dikirim langsung ke Telegram

### 📊 Ringkasan & Rekap
- `/debts` — daftar semua utang
- `/monthly` — rekap bulan ini
- `/upcoming` — utang 30 hari ke depan
- `/summary` — ringkasan cepat

### 🧱 Lengkap
- Multi-user
- Support cicilan (misal: 3/12)
- Kategori utang
- Riwayat OCR log
- PostgreSQL + SQLAlchemy async
- Migrasi database dengan Alembic

---

## 🏗️ Arsitektur

```
app/
├── core/           # Config, DB, Scheduler
├── models/         # SQLAlchemy models (User, Debt, Reminder, OcrLog)
├── schemas/        # Pydantic schemas
├── services/       # Business logic (debt, ocr, ai parser)
├── platforms/      # Platform adapters
│   └── telegram/   # Aiogram bot (handlers, keyboards)
└── main.py         # FastAPI app + lifespan
```

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| API | FastAPI 0.115+ |
| Bot | Aiogram 3.17+ |
| Database | PostgreSQL (asyncpg) + SQLAlchemy 2.0 async |
| Migrasi | Alembic |
| OCR | PaddleOCR (dengan model bahasa Indonesia) |
| AI | DeepSeek Chat API (structured extraction) |
| Scheduler | APScheduler |
| Container | Docker |
| Minimum Python | 3.12 |

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/FMATheNomad/jatuhtempo.git
cd jatuhtempo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Konfigurasi

```bash
cp .env.example .env
# Isi .env dengan:
# - DEEPSEEK_API_KEY: untuk parsing AI
# - TELEGRAM_BOT_TOKEN: token dari @BotFather
# - DATABASE_URL: koneksi PostgreSQL
```

### 3. Database

```bash
# Buat database PostgreSQL
createdb jatuhtempo

# Jalankan migrasi
alembic upgrade head
```

### 4. Jalankan

```bash
uvicorn app.main:app --reload
```

Bot Telegram akan otomatis mulai polling. API berjalan di `http://localhost:8000`.

### Docker

```bash
docker build -t jatuhtempo -f docker/Dockerfile .
docker run -p 8000:8000 --env-file .env jatuhtempo
```

---

## 📱 Perintah Telegram

| Perintah | Fungsi |
|----------|--------|
| `/start` | Mulai bot |
| `/help` | Bantuan |
| `/add <platform> <amount> <YYYY-MM-DD>` | Tambah utang manual |
| `/debts` | Lihat semua utang |
| `/monthly` | Rekap bulan ini |
| `/upcoming` | Utang 30 hari ke depan |
| `/summary` | Ringkasan singkat |

Atau cukup **kirim screenshot** tagihan — bot akan OCR + parse otomatis.

---

## 🔌 API Endpoints

| Method | Path | Deskripsi |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/api/debts` | Tambah utang |
| GET | `/api/debts/{user_id}` | Daftar utang user |
| GET | `/api/debts/{user_id}/summary` | Ringkasan bulanan |
| POST | `/api/ocr` | OCR + parse screenshot |

---

## 🧪 Environment Variables

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `APP_NAME` | JatuhTempo | Nama aplikasi |
| `DATABASE_URL` | postgresql+asyncpg://... | Koneksi database |
| `DEEPSEEK_API_KEY` | — | API key untuk AI parsing |
| `DEEPSEEK_MODEL` | deepseek-chat | Model DeepSeek |
| `TELEGRAM_BOT_TOKEN` | — | Token bot Telegram |
| `MEDIA_DIR` | media | Direktori penyimpanan gambar sementara |
| `MAX_IMAGE_SIZE_MB` | 10 | Maksimal ukuran gambar |
| `REMINDER_CHECK_INTERVAL_MINUTES` | 1 | Interval pengecekan pengingat |

---

## 🗺️ Roadmap

- [ ] Platform lain: WhatsApp, Web dashboard
- [ ] Multi-bank & e-wallet detection
- [ ] Payment reminder via email
- [ ] Laporan PDF bulanan
- [ ] Shared debt / group tracking
- [ ] Integrasi dengan payment gateway

---

## 📄 Lisensi

All Rights Reserved — © 2026 FMATheNomad
