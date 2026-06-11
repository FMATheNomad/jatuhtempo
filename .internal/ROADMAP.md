# JatuhTempo — Riset Pasar & Roadmap Inovasi

**Tanggal:** Juni 2026
**Produk acuan:** JatuhTempo — AI-Powered Debt Management Assistant
**Ekosistem:** Komunitas Bebas Utang (KOMBAT) — Guru Gembul

---

## Posisi JatuhTempo di Pasar

### Kesimpulan Utama

**JatuhTempo unik.** Tidak ada satu pun produk di dunia yang menggabungkan OCR screenshot tagihan, AI parsing, bot multi-platform (Telegram/Web/WhatsApp), dan debt tracking spesifik paylater/pinjol dalam satu produk. Di Indonesia khususnya, ini **blue ocean** — tidak ada kompetitor lokal yang relevan.

### Skor Kompetitif (1-10)

| Area | Skor | Keterangan |
|------|------|------------|
| Debt Capture (OCR + AI) | 9/10 | Sangat kuat, pembeda utama |
| Debt Tracking | 8/10 | CRUD lengkap, multi-platform |
| Reminder System | 8.5/10 | APScheduler, lifecycle lengkap |
| AI Intelligence | 7/10 | Parsing + NL input + learning |
| Predictive Analytics | 3/10 | Belum ada |
| Behavioral Finance | 2/10 | Belum ada |
| Opportunity Network | 1/10 | Baru ide (terintegrasi KOMBAT) |
| Monetization Readiness | 7/10 | Polar.sh terintegrasi |
| Market Differentiation | 9/10 | Biru di Indonesia, biru di global |

### Celah Pasar Global

Mayoritas kompetitor global melakukan **"Tracking Debt"**. Tidak ada yang benar-benar melakukan **"Preventing Financial Failure"** apalagi **"Providing Financial Opportunity"**. JatuhTempo punya kesempatan menjadi **AI Debt Operating System**, bukan sekadar tracker.

---

## Kompetitor Relevan

| Produk | Keunggulan Mereka | Keunggulan JatuhTempo |
|--------|-------------------|----------------------|
| **DebtErasr** (US) | AI payoff strategy, credit score | Telegram, OCR lifecycle, Indonesia use case |
| **DebtPilot AI** | AI payoff optimization | OCR, screenshot parsing, messaging platform |
| **BillSnap** | OCR + bill reminder | Debt lifecycle, installment tracking, NL input |
| **Undebt.it** | Snowball/avalanche calculator | AI, OCR, reminder, multi-platform — jauh lebih advanced |
| **Bright Money** | Otomatisasi pembayaran | US-only, no OCR, no bot |
| **KOMBAT (komunitas)** | Opportunity network, gotong royong | Belum ada digital platform-nya — INI CELAH KITA |

---

## Matriks Perbandingan Fitur

| Fitur | JatuhTempo | Kompetitor |
|-------|------------|------------|
| OCR Screenshot | ✅ | ⚠️ Sebagian |
| AI Parsing | ✅ | ⚠️ |
| Telegram Bot | ✅ | ❌ |
| Multi-Platform | ✅ | ❌ |
| Debt Reminder Lifecycle | ✅ | ⚠️ |
| Installment Tracking | ✅ | ⚠️ |
| Interest Rate Tracking | ✅ | ❌ |
| AI Learning (per platform) | ✅ | ❌ |
| Natural Language Input | ✅ | ❌ |
| AI Debt Advisor | ❌ | ✅ Sebagian |
| Opportunity Network | 🚧 **KOMBAT** | ❌ |
| Credit Score | ❌ | ✅ |
| Predictive Risk | ❌ | ⚠️ |

---

## Katalog Inovasi Masa Depan

### 🟢 Fase 1: Build Sekarang ✅ (High Impact, Low Effort)

Semua sudah selesai:
- ✅ Debt Payoff Strategy Engine
- ✅ Simulator Tanggal Bebas Utang (Indonesia Context)
- ✅ Batch OCR Scanner
- ✅ Interest rate tracking + AI learning per platform
- ✅ Natural language input (bot + web)
- ✅ AI platform rate learning (EMA decay, outlier detection, majority vote)
- ✅ Auto-suggest bunga di form & bot
- ✅ Admin rates management page
- ✅ Production hardening (25 security + migration fixes)
- ✅ Demo account untuk testing

### 🟡 Fase 2: Pasca Monetisasi (Medium Impact, Medium Effort)

#### 1. Behavioral Nudge Engine
**Deskripsi:** AI pelajari kapan user biasanya gagal bayar — minggu ketiga? setelah gajian? platform tertentu? Kirim nudge personal: "Minggu ini kamu biasanya skip Kredivo — sudah ada Rp350rb cicilan ke-4 dari 12."
**Estimasi:** 7-10 hari

#### 2. Personal Debt Health Score ★
**Deskripsi:** Mini version dari ide besar. Skor A-E berdasarkan data pribadi user: rasio utang/pendapatan, frekuensi terlambat, jumlah platform aktif. Output: "Aman" / "Waspada" / "Bahaya" + saran AI.
**Estimasi:** 3-5 hari

#### 3. Peluang — Opportunity Network (KOMBAT) ★
**Deskripsi:** Fitur yang menghubungkan anggota KOMBAT dengan peluang nyata dari para pihak yang ingin membantu. Peluang diposting oleh pengguna terverifikasi (orang kaya raya, pemilik bisnis, dll). Jenis peluang: pekerjaan lepas, pelatihan skill, modal usaha kecil, reseller opportunity, affiliate program.

**Arsitektur:**
```
┌─ Peluang ─────────────────────────────────┐
│  Judul: "Dibutuhkan 10 reseller frozen food"│
│  Deskripsi: "Modal Rp500rb, estimasi       │
│  profit Rp200rb/bulan. Bimbingan gratis."  │
│  Diposting oleh: Verified Business #042    │
│  Deadline: 30 Juni 2026                    │
│  Sisa kuota: 7 dari 10                     │
│                                            │
│  [ 💼 Ambil Peluang Ini ]                  │
│                                            │
│  Catatan: JatuhTempo hanya penyedia        │
│  platform. Transaksi di luar tanggung jawab │
│  kami.                                     │
└────────────────────────────────────────────┘
```

**Model Bisnis:** 
- Gratis untuk user KOMBAT
- Revenue share opsional: jika user berhasil dapat penghasilan lewat peluang, donasi sukarela untuk JatuhTempo
- Verified badge untuk pemberi peluang (biaya verifikasi)

**Estimasi:** 7-10 hari (MVP)
**Integrasi dengan KOMBAT:** Postingan dari komunitas bisa masuk secara manual (admin) atau via API nantinya.

#### 4. WhatsApp Bot
Full parity dengan Telegram bot — /add, /debts, reminder, semuanya via WhatsApp.
**Estimasi:** 14-21 hari

#### 5. Calendar Sync
Due dates muncul di Google Calendar, iCloud, Outlook.
**Estimasi:** 3-5 hari

### 🔴 Fase 3: Masa Depan (High Impact, High Effort)

#### 6. Debt Favorability Index ★ (Ide Besar)
**Deskripsi:** Menggabungkan Personal Debt Health Score (mikro) + data makro ekonomi Indonesia untuk jawab: "Apakah kondisi saat ini cocok ambil utang?"

Input:
- **Personal:** skor utang, riwayat bayar, kapasitas bayar
- **Makro:** suku bunga BI, inflasi, kurs USD/IDR, tren bunga pinjol
- **Regulasi:** kebijakan OJK terbaru

Output: Skor A-E + penjelasan AI dalam bahasa Indonesia.

**Estimasi:** 14-21 hari
**Catatan:** Perlu sumber data makro yang reliable. Manual update bulanan via admin panel cukup untuk MVP.

#### 7. AI Debt Autopilot™
User cukup upload screenshot. AI otomatis: detect lender → detect due date → detect installment → detect risk → generate payment plan → generate reminder schedule. Tanpa user mengisi form.
**Estimasi:** 30+ hari

#### 8. Debt Stress Score™
Bukan financial score — psychological score. AI deteksi tingkat stres berdasarkan jumlah debt, overdue frequency, debt growth rate, reminder ignored rate.
**Estimasi:** 14-21 hari

#### 9. Debt Negotiation Copilot™
AI bantu user negosiasi dengan lender. Generate script WA/email/telepon: "Halo, saya mengalami kendala sementara. Apakah tersedia restrukturisasi..."
**Estimasi:** 14-21 hari

#### 10. Internal Credit Health Score
Proxy score 0-100 berdasarkan data behavioral internal.
**Estimasi:** 14-21 hari

#### 11. Debt Buddy — Anonymous Community
Cohort anonim — user bergabung ke kelompok dengan profil utang serupa. "Rata-rata cohort kamu melunasi 19% utang dalam 2 bulan. Kamu di 24%."
**Estimasi:** 21-30 hari

---

## Game Changers Utama (Prioritas)

### Game Changer #1: Peluang — Opportunity Network (KOMBAT) ← BARU
Ini yang membedakan JatuhTempo dari APAPUN di pasar global. Bukan sekadar debt tracker — tapi jembatan antara yang punya masalah dan yang punya solusi. Terintegrasi dengan komunitas nyata (KOMBAT).

### Game Changer #2: Behavioral Nudge Engine
Bukan reminder biasa. AI yang belajar pola "slip" individual.

### Game Changer #3: Debt Favorability Index
Menggabungkan personal + makro. Belum ada yang lakukan ini di consumer finance.

### Game Changer #4: Debt Buddy — Anonymous Community
Aspek psikologis — utang itu memalukan, komunitas anonim adalah antidotnya.

---

## Rekomendasi Jalur Pengembangan

```
Fase 1 (selesai ✅)
├── Strategy Engine ✅
├── OCR + AI Parsing ✅
├── Simulator ✅
├── Interest Rate + AI Learning ✅
├── NL Input (bot + web) ✅
├── Production Hardening ✅
└── Demo Account ✅

Fase 2 (setelah monetisasi — 1-2 bulan)
├── Behavioral Nudge Engine ⭐
├── Personal Debt Health Score ⭐
├── PELUANG — Opportunity Network ⭐⭐ TERINTEGRASI KOMBAT
├── WhatsApp Bot
└── Calendar Sync

Fase 3 (3-6 bulan)
├── Debt Favorability Index ⭐⭐ (Mikro + Makro)
├── AI Debt Autopilot
├── Debt Stress Score
├── Debt Negotiation Copilot
├── Internal Credit Health Score
└── Debt Buddy Anonymous Community
```

---

## Catatan Strategis

1. **Monetisasi dulu, baru fitur canggih.** Jangan bangun AI advisor sebelum payment gateway hidup.
2. **Peluang (KOMBAT) adalah moat berikutnya.** OCR menarik user. Peluang bikin user stay.
3. **OCR adalah moat pertama.** Semakin banyak user upload screenshot, semakin bagus dataset untuk training model deteksi platform Indonesia.
4. **Telegram-first adalah keunikan.** Jangan tinggalkan. Tambah WhatsApp jangan replace Telegram.
5. **"Preventing Financial Failure" > "Tracking Debt".** Ini positioning yang bikin JatuhTempo beda dari kompetitor global.
6. **"Providing Financial Opportunity" > "Preventing Financial Failure".** Ini vision jangka panjang.
7. **Indonesia dulu.** Dapetin product-market fit di Indonesia, baru scale ke SEA.
