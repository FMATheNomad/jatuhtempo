import Link from 'next/link'

export default function GettingStartedPage() {
  return (
    <div className="min-h-screen bg-background">
      <section className="gradient-hero text-white">
        <div className="max-w-3xl mx-auto px-6 py-16 md:py-20 text-center">
          <h1 className="text-3xl md:text-5xl font-bold mb-4 animate-fade-in">Panduan Memulai</h1>
          <p className="text-white/60 text-lg max-w-lg mx-auto animate-fade-in">Buat akun, tambah utang pertama, hubungkan Telegram, dan atur pengingat.</p>
        </div>
      </section>

      <div className="max-w-3xl mx-auto px-4 lg:px-6 py-12">
        <h2 className="text-2xl font-bold mb-4">Selamat datang di JatuhTempo!</h2>
        <p className="text-muted-foreground mb-6">Berikut panduan cepat untuk memulai.</p>

        <h3 className="text-xl font-semibold mt-8 mb-3">1. Buat Akun</h3>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-6">
          <li>Buka <Link href="/login" className="text-accent hover:underline">halaman Login</Link> dan pilih <strong>Daftar</strong>.</li>
          <li>Masukkan nama, email, dan password.</li>
          <li>Setelah mendaftar, kamu akan langsung masuk ke dashboard.</li>
        </ol>

        <h3 className="text-xl font-semibold mt-8 mb-3">2. Tambah Utang Pertama</h3>
        <h4 className="font-semibold mt-4 mb-2">Cara Manual</h4>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-4">
          <li>Di dashboard, isi form <strong>Tambah Utang Cepat</strong>.</li>
          <li>Masukkan nama platform.</li>
          <li>Masukkan jumlah tagihan.</li>
          <li>Pilih tanggal jatuh tempo.</li>
          <li>Klik <strong>Tambah</strong>.</li>
        </ol>

        <h4 className="font-semibold mt-4 mb-2">Cara OCR</h4>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-6">
          <li>Klik tombol upload di halaman Utang.</li>
          <li>Pilih screenshot tagihan.</li>
          <li>AI akan membaca dan mengisi data secara otomatis.</li>
          <li>Verifikasi dan simpan.</li>
        </ol>

        <h3 className="text-xl font-semibold mt-8 mb-3">3. Hubungkan Telegram</h3>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-6">
          <li>Buka <Link href="/settings" className="text-accent hover:underline">Pengaturan</Link>.</li>
          <li>Klik <strong>Buka Bot Telegram</strong>.</li>
          <li>Di Telegram, kirim <code className="bg-secondary px-1 rounded">/login</code>.</li>
          <li>Klik link yang dikirim bot.</li>
        </ol>

        <h3 className="text-xl font-semibold mt-8 mb-3">4. Atur Pengingat</h3>
        <p className="text-muted-foreground mb-2">Pengingat otomatis dikirim H-7, H-3, H-1, dan hari H.</p>

        <h3 className="text-xl font-semibold mt-8 mb-3">5. Pantau Dashboard</h3>
        <p className="text-muted-foreground mb-2">Dashboard menampilkan total utang aktif, yang sudah dibayar, terlambat, ringkasan kategori, dan utang terbaru.</p>

        <h3 className="text-xl font-semibold mt-8 mb-3">Tips</h3>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground">
          <li>Gunakan kategori untuk mengelompokkan utang.</li>
          <li>Update status pembayaran segera setelah membayar.</li>
          <li>Hubungkan WhatsApp untuk notifikasi cadangan.</li>
        </ul>
      </div>

      <footer className="border-t py-8 px-6 text-center text-sm text-muted-foreground">
        <div className="max-w-3xl mx-auto">
          <Link href="/" className="text-accent hover:underline text-sm">{"<"}-- Kembali ke Beranda</Link>
          <div className="flex items-center justify-center gap-4 mt-3 mb-4">
            <Link href="/faq" className="hover:text-foreground transition-colors">FAQ</Link>
            <span className="text-border">.</span>
            <Link href="/legal/terms" className="hover:text-foreground transition-colors">Terms</Link>
            <span className="text-border">.</span>
            <Link href="/legal/privacy" className="hover:text-foreground transition-colors">Privacy</Link>
            <span className="text-border">.</span>
            <Link href="/docs" className="hover:text-foreground transition-colors">Docs</Link>
          </div>
          <p>{"©"} 2026 FMA Software Labs. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}