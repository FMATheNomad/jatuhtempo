# 🧠 JatuhTempo

> **PROPRIETARY SOFTWARE — All Rights Reserved**
> 
> This repository is provided for **authorized personnel only**.  
> Unauthorized copying, distribution, or use is strictly prohibited.
> 
> See [LICENSE](LICENSE) for full terms.

---

**JatuhTempo** — AI-powered debt management assistant.  
Multi-platform: Telegram bot & Web dashboard.

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

---

## 📄 Lisensi

**PROPRIETARY SOFTWARE** — See [LICENSE](LICENSE) for full terms.  
© 2026 FMATheNomad. All rights reserved.
