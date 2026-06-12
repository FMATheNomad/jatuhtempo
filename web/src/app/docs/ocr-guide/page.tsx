import Link from 'next/link'

export default function OcrGuidePage() {
  return (
    <div className="min-h-screen bg-background">
      <section className="gradient-hero text-white">
        <div className="max-w-3xl mx-auto px-6 py-16 md:py-20 text-center">
          <h1 className="text-3xl md:text-5xl font-bold mb-4 animate-fade-in">Panduan OCR</h1>
          <p className="text-white/60 text-lg max-w-lg mx-auto animate-fade-in">Cara upload screenshot tagihan dan optimasi hasil bacaan AI.</p>
        </div>
      </section>

      <div className="max-w-3xl mx-auto px-4 lg:px-6 py-12">
        <p className="text-muted-foreground mb-6">Fitur OCR JatuhTempo memungkinkan kamu memotret atau upload screenshot tagihan dan AI akan membaca datanya secara otomatis.</p>

        <h3 className="text-xl font-semibold mt-8 mb-3">Melalui Web</h3>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-6">
          <li>Di halaman Utang, klik <strong>Upload Screenshot</strong>.</li>
          <li>Pilih file gambar (JPG, PNG, WEBP).</li>
          <li>AI akan memproses gambar dalam beberapa detik.</li>
          <li>Periksa hasil: platform, jumlah, tanggal jatuh tempo.</li>
          <li>Jika sesuai, klik <strong>Simpan</strong>.</li>
        </ol>

        <h3 className="text-xl font-semibold mt-8 mb-3">Melalui Telegram</h3>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-6">
          <li>Buka chat dengan <code className="bg-secondary px-1 rounded">@JatuhTempo_bot</code>.</li>
          <li>Kirim foto tagihan langsung ke chat.</li>
          <li>Bot akan membalas dengan data yang terbaca.</li>
          <li>Konfirmasi untuk menyimpan.</li>
        </ol>

        <h3 className="text-xl font-semibold mt-8 mb-3">Tips Terbaik</h3>
        <ul className="list-disc list-inside space-y-2 text-muted-foreground mb-6">
          <li><strong>Cahaya cukup</strong> — pastikan tagihan terang dan tidak silau.</li>
          <li><strong>Fokus tajam</strong> — hindari foto blur.</li>
          <li><strong>Seluruh tagihan</strong> — pastikan semua informasi masuk frame.</li>
          <li>OCR optimal dengan screenshot digital dan tagihan cetak yang jelas.</li>
        </ul>

        <h3 className="text-xl font-semibold mt-8 mb-3">Format Didukung</h3>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground mb-6">
          <li>Screenshot aplikasi (GoPay Later, Shopee PayLater, Akulaku, dll.)</li>
          <li>Foto tagihan cetak (kartu kredit, listrik, air)</li>
        </ul>

        <h3 className="text-xl font-semibold mt-8 mb-3">Batasan</h3>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground">
          <li>Maksimum 5MB per gambar</li>
          <li>Bahasa: Indonesia dan Inggris</li>
          <li>Akurasi ~95% untuk gambar jelas</li>
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