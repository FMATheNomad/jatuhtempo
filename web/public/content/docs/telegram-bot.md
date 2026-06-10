# Panduan Bot Telegram

Bot Telegram JatuhTempo memungkinkan kamu mengelola utang langsung dari Telegram.

## Mulai

1. Cari `@JatuhTempo_bot` di Telegram.
2. Kirim `/start` untuk memulai.
3. Kirim `/login` untuk menghubungkan akunmu.
4. Klik link yang dikirim bot untuk otorisasi.

## Perintah Tersedia

| Perintah | Deskripsi |
|----------|-----------|
| `/start` | Memulai bot |
| `/login` | Login / tautkan akun |
| `/debts` | Lihat daftar utang |
| `/summary` | Ringkasan semua utang |
| `/add` | Tambah utang baru (interaktif) |
| `/pay <id>` | Tandai utang sebagai lunas |
| `/help` | Bantuan |

## Menambahkan Utang via Bot

1. Kirim `/add`.
2. Bot akan meminta informasi secara bertahap:
   - Nama platform
   - Jumlah tagihan
   - Tanggal jatuh tempo (YYYY-MM-DD)
   - Kategori (opsional)
3. Konfirmasi data yang dimasukkan.

## Notifikasi

Bot akan mengirim notifikasi otomatis:
- **Pengingat pembayaran** sesuai jadwal
- **Konfirmasi** setelah menambah / membayar utang
- **Ringkasan mingguan** setiap hari Senin

## Tips

- Simpan chat bot di bagian atas Telegram agar tidak terlewat.
- Gunakan `/pay <id>` cepat untuk menandai lunas.
- Cek ID utang dari daftar `/debts`.
