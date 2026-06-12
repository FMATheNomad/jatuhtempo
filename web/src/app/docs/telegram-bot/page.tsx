import Link from 'next/link'

export default function TelegramBotPage() {
  return (
    <div className="min-h-screen bg-background">
      <section className="gradient-hero text-white">
        <div className="max-w-3xl mx-auto px-6 py-16 md:py-20 text-center">
          <h1 className="text-3xl md:text-5xl font-bold mb-4 animate-fade-in">Bot Telegram</h1>
          <p className="text-white/60 text-lg max-w-lg mx-auto animate-fade-in">Kelola utang langsung dari Telegram. Semua perintah dan cara pakai.</p>
        </div>
      </section>

      <div className="max-w-3xl mx-auto px-4 lg:px-6 py-12">
        <p className="text-muted-foreground mb-6">Bot Telegram JatuhTempo memungkinkan kamu mengelola utang langsung dari Telegram.</p>

        <h3 className="text-xl font-semibold mt-8 mb-3">Mulai</h3>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-6">
          <li>Cari <code className="bg-secondary px-1 rounded">@JatuhTempo_bot</code> di Telegram.</li>
          <li>Kirim <code className="bg-secondary px-1 rounded">/start</code> untuk memulai.</li>
          <li>Kirim <code className="bg-secondary px-1 rounded">/login</code> untuk menghubungkan akun.</li>
          <li>Klik link yang dikirim bot untuk otorisasi.</li>
        </ol>

        <h3 className="text-xl font-semibold mt-8 mb-3">Perintah Tersedia</h3>
        <div className="overflow-x-auto mb-6">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-secondary">
                <th className="text-left p-2 border">Perintah</th>
                <th className="text-left p-2 border">Deskripsi</th>
              </tr>
            </thead>
            <tbody>
              <tr><td className="p-2 border"><code className="bg-secondary px-1 rounded">/start</code></td><td className="p-2 border text-muted-foreground">Memulai bot</td></tr>
              <tr><td className="p-2 border"><code className="bg-secondary px-1 rounded">/login</code></td><td className="p-2 border text-muted-foreground">Tautkan akun</td></tr>
              <tr><td className="p-2 border"><code className="bg-secondary px-1 rounded">/debts</code></td><td className="p-2 border text-muted-foreground">Lihat daftar utang</td></tr>
              <tr><td className="p-2 border"><code className="bg-secondary px-1 rounded">/summary</code></td><td className="p-2 border text-muted-foreground">Ringkasan utang</td></tr>
              <tr><td className="p-2 border"><code className="bg-secondary px-1 rounded">/add</code></td><td className="p-2 border text-muted-foreground">Tambah utang baru</td></tr>
              <tr><td className="p-2 border"><code className="bg-secondary px-1 rounded">/pay</code></td><td className="p-2 border text-muted-foreground">Tandai lunas</td></tr>
              <tr><td className="p-2 border"><code className="bg-secondary px-1 rounded">/help</code></td><td className="p-2 border text-muted-foreground">Bantuan</td></tr>
            </tbody>
          </table>
        </div>

        <h3 className="text-xl font-semibold mt-8 mb-3">Menambahkan Utang via Bot</h3>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-6">
          <li>Kirim <code className="bg-secondary px-1 rounded">/add</code>.</li>
          <li>Bot akan meminta informasi: nama platform, jumlah, tanggal, kategori.</li>
          <li>Konfirmasi data yang dimasukkan.</li>
        </ol>

        <h3 className="text-xl font-semibold mt-8 mb-3">Notifikasi</h3>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground mb-6">
          <li>Pengingat pembayaran sesuai jadwal</li>
          <li>Konfirmasi setelah menambah / membayar utang</li>
          <li>Ringkasan mingguan setiap hari Senin</li>
        </ul>

        <h3 className="text-xl font-semibold mt-8 mb-3">Tips</h3>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground">
          <li>Pin chat bot di atas Telegram agar tidak terlewat.</li>
          <li>Cek ID utang dari daftar <code className="bg-secondary px-1 rounded">/debts</code>.</li>
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