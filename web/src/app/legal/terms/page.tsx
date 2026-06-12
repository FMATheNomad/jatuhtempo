import Link from 'next/link'
import type { Metadata } from 'next'
import { ArrowLeft } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Syarat & Ketentuan — JatuhTempo',
  description: 'Syarat dan ketentuan penggunaan layanan JatuhTempo',
}

const sections = [
  {
    title: '1. Penerimaan Syarat',
    content:
      'Dengan menggunakan aplikasi JatuhTempo ("Platform"), Anda menyetujui syarat dan ketentuan ini. Jika Anda tidak setuju, jangan gunakan Platform.',
  },
  {
    title: '2. Deskripsi Layanan',
    content:
      'JatuhTempo adalah platform manajemen utang yang menyediakan pencatatan dan pelacakan utang, OCR otomatis untuk membaca tagihan, pengingat pembayaran via Telegram dan WhatsApp, dashboard analitik real-time, serta fitur lain yang ditambahkan dari waktu ke waktu.',
  },
  {
    title: '3. Akun Pengguna',
    content:
      '3.1 Anda bertanggung jawab menjaga kerahasiaan kredensial akun.\n3.2 Anda harus berusia minimal 17 tahun atau memiliki izin orang tua.\n3.3 Satu akun hanya untuk satu orang — tidak boleh dibagikan.',
  },
  {
    title: '4. Langganan dan Pembayaran',
    content:
      '4.1 Layanan dasar gratis dengan batasan tertentu.\n4.2 Langganan Pro adalah pembayaran berulang (bulanan/tahunan).\n4.3 Pembatalan dapat dilakukan kapan saja; akses Pro tetap aktif sampai akhir periode.\n4.4 Harga dapat berubah dengan pemberitahuan 30 hari.',
  },
  {
    title: '5. Penggunaan yang Wajar',
    content:
      'Anda setuju untuk tidak menyalahgunakan sistem OCR untuk tujuan ilegal, mengakses data pengguna lain, melakukan reverse engineering pada Platform, atau menggunakan bot atau skrip otomatis yang mengganggu layanan.',
  },
  {
    title: '6. Batasan Tanggung Jawab',
    content:
      'JatuhTempo disediakan "sebagaimana adanya". Kami tidak bertanggung jawab atas keputusan keuangan yang Anda buat berdasarkan data di Platform, kerugian akibat keterlambatan notifikasi, atau gangguan layanan di luar kendali kami.',
  },
  {
    title: '7. Pengakhiran',
    content:
      'Kami dapat menangguhkan atau menghentikan akun jika melanggar syarat ini. Anda dapat berhenti menggunakan Platform kapan saja.',
  },
  {
    title: '8. Perubahan Syarat',
    content:
      'Kami dapat memperbarui syarat ini kapan saja. Perubahan signifikan akan diberitahukan melalui email atau notifikasi di Platform.',
  },
]

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 pt-6">
        <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground/60 hover:text-accent transition-all duration-200 group">
          <span className="flex items-center justify-center w-8 h-8 rounded-full border border-border bg-card hover:bg-accent/5 hover:border-accent/30 transition-all duration-200 group-hover:-translate-x-0.5">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </span>
          <span className="hidden sm:inline">Kembali</span>
        </Link>
      </div>
      {/* Hero */}
      <section className="gradient-hero text-white">
        <div className="max-w-3xl mx-auto px-6 py-16 md:py-24 text-center">
          <h1 className="text-3xl md:text-5xl font-bold mb-4 animate-fade-in">
            Syarat & Ketentuan
          </h1>
          <p className="text-white/60 text-lg max-w-lg mx-auto animate-fade-in">
            Terakhir diperbarui: 11 Juni 2026
          </p>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-4 lg:px-6 py-12 space-y-8 animate-fade-in">
        {sections.map((section) => (
          <div key={section.title}>
            <h2 className="text-lg font-semibold mb-3">{section.title}</h2>
            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
              {section.content}
            </p>
          </div>
        ))}

        {/* Contact */}
        <div className="border border-border rounded-2xl p-4 md:p-8 bg-card text-center">
          <h2 className="font-semibold text-lg mb-2">Kontak</h2>
          <p className="text-sm text-muted-foreground">
            Email:{' '}
            <a href="mailto:fmasoftwarelabs@gmail.com" className="text-accent hover:underline">
              fmasoftwarelabs@gmail.com
            </a>
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 px-6 text-center text-sm text-muted-foreground">
        <div className="flex items-center justify-center gap-4 mb-4">
          <Link href="/faq" className="hover:text-foreground transition-colors">FAQ</Link>
          <span className="text-border">•</span>
          <Link href="/legal/terms" className="hover:text-foreground transition-colors">Terms</Link>
          <span className="text-border">•</span>
          <Link href="/legal/privacy" className="hover:text-foreground transition-colors">Privacy</Link>
          <span className="text-border">•</span>
          <Link href="/docs" className="hover:text-foreground transition-colors">Docs</Link>
        </div>
        <p>© {new Date().getFullYear()} JatuhTempo. All rights reserved.</p>
      </footer>
    </div>
  )
}
