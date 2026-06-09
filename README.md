# 🧠 JatuhTempo — AI-Powered Debt Management Assistant

<p align="center">
  <img src="https://jatuhtempo.up.railway.app/assets/logo.webp" width="200" alt="JatuhTempo Logo"/>
</p>

<p align="center">
  <b>Kelola utang paylater, pinjol, kartu kredit — dari Telegram atau Web.</b><br/>
  OCR otomatis, AI parsing, pengingat cerdas, dan strategi pelunasan.
</p>

<p align="center">
  <a href="https://jatuhtempo.up.railway.app"><img src="https://img.shields.io/badge/Live-Dashboard-0a0b1e?style=for-the-badge" alt="Live"/></a>
  <a href="https://t.me/JatuhTempo_bot"><img src="https://img.shields.io/badge/Telegram-Bot-0088cc?style=for-the-badge&logo=telegram" alt="Telegram Bot"/></a>
  <a href="https://github.com/FMATheNomad/jatuhtempo/issues"><img src="https://img.shields.io/github/issues/FMATheNomad/jatuhtempo?style=for-the-badge" alt="Issues"/></a>
  <a href="https://github.com/FMATheNomad/jatuhtempo/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=for-the-badge" alt="License"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-blue?logo=python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi"/>
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql"/>
  <img src="https://img.shields.io/badge/Railway-deployed-0b0d0e?logo=railway"/>
</p>

---

**JatuhTempo** adalah asisten manajemen utang berbasis AI untuk pengguna Indonesia dan global. Multi-platform — Telegram bot, Web dashboard, dan rencana WhatsApp.

Kirim screenshot tagihan → AI baca otomatis (OCR + DeepSeek) → catat jumlah, platform, jatuh tempo. Dapatkan pengingat H-7, H-3, H-1, due, overdue langsung ke Telegram. Lengkap dengan strategi pelunasan (snowball) dan simulasi bebas utang.

---

## ✨ Fitur

### 📸 OCR + AI Parsing
- Upload screenshot tagihan → Tesseract OCR baca teks → DeepSeek AI ekstrak data terstruktur
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

## 📊 Status Proyek

| Area | Status |
|------|--------|
| **Telegram Bot** | ✅ Production — /add, /debts, /edit, /delete, /history, /strategy, OCR, pengingat |
| **Web Dashboard** | ✅ Live — CRUD utang, OCR upload, strategi snowball, simulasi bebas utang |
| **OCR + AI Parsing** | ✅ Production — Tesseract + DeepSeek API + platform signature matching |
| **Pengingat** | ✅ H-7, H-3, H-1, due, overdue via Telegram |
| **Auth** | ✅ Email/password + Telegram linking + JWT |
| **Mobile** | ✅ Responsive, 44px touch targets, card list |
| **Payment** | 🚧 Polar.sh terintegrasi, belum aktif |
| **WhatsApp** | 🚧 Rencana |

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
| OCR | Tesseract OCR (pytesseract) |
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
docker build -t jatuhtempo .
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
| `DEEPSEEK_MODEL` | deepseek-v4-flash | Model DeepSeek |
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
