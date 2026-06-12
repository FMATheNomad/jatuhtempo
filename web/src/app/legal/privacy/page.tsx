import Link from 'next/link'
import type { Metadata } from 'next'
import { ArrowLeft } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Kebijakan Privasi — JatuhTempo',
  description: 'Kebijakan privasi dan perlindungan data JatuhTempo',
}

const sections = [
  {
    title: '1. Informasi yang Kami Kumpulkan',
    content: [
      ['Informasi Akun', 'Nama, alamat email, nomor telepon (opsional untuk WhatsApp), dan ID Telegram.'],
      ['Data Utang', 'Informasi tagihan yang Anda masukkan: nama platform, jumlah, tanggal jatuh tempo, kategori, catatan, dan screenshot tagihan.'],
      ['Data Penggunaan', 'Log aktivitas, interaksi dengan bot Telegram, dan metrik penggunaan fitur.'],
    ],
  },
  {
    title: '2. Cara Kami Menggunakan Informasi',
    content: [
      null,
      'Menyediakan dan memelihara layanan manajemen utang, mengirim pengingat pembayaran sesuai jadwal, meningkatkan akurasi OCR dan fitur AI, menganalisis penggunaan untuk pengembangan produk, serta komunikasi terkait akun dan pembaruan layanan.',
    ],
  },
  {
    title: '3. Penyimpanan Data',
    content: [
      null,
      'Data Anda disimpan di server yang aman dengan enkripsi. Kami menyimpan data selama akun Anda aktif. Setelah akun dihapus, data akan dihapus dalam 30 hari.',
    ],
  },
  {
    title: '4. Berbagi Data',
    content: [
      null,
      'Kami TIDAK menjual data pribadi Anda ke pihak ketiga. Data dapat dibagikan dengan penyedia infrastruktur cloud (untuk hosting), penyedia OCR/AI (untuk pemrosesan gambar, tanpa menyimpan data), dan pihak berwenang jika diwajibkan oleh hukum.',
    ],
  },
  {
    title: '5. Keamanan',
    content: [
      null,
      'Kami menerapkan enkripsi SSL/TLS untuk semua transmisi data, enkripsi database, otentikasi dua faktor (via Telegram), dan audit keamanan berkala.',
    ],
  },
  {
    title: '6. Hak Anda',
    content: [
      null,
      'Anda berhak untuk mengakses data pribadi Anda, memperbaiki data yang tidak akurat, menghapus akun dan data Anda, mengekspor data Anda (tersedia untuk pengguna Pro), dan menolak pengumpulan data tertentu.',
    ],
  },
  {
    title: '7. Cookie',
    content: [
      null,
      'Kami menggunakan cookie esensial untuk autentikasi sesi. Kami tidak menggunakan cookie pelacakan pihak ketiga.',
    ],
  },
  {
    title: '8. Perubahan Kebijakan',
    content: [
      null,
      'Perubahan pada kebijakan privasi akan diberitahukan melalui email atau notifikasi di Platform.',
    ],
  },
]

export default function PrivacyPage() {
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
            Kebijakan Privasi
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
            {section.content[0] ? (
              <div className="space-y-3">
                {section.content.map((item, i) => {
                  if (!item) return null
                  if (typeof item === 'string') {
                    return (
                      <p key={i} className="text-sm text-muted-foreground leading-relaxed">
                        {item}
                      </p>
                    )
                  }
                  const [label, desc] = item
                  return (
                    <div key={label}>
                      <p className="font-medium text-sm">{label}</p>
                      <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground leading-relaxed">
                {section.content[1]}
              </p>
            )}
          </div>
        ))}

        {/* Contact */}
        <div className="border border-border rounded-2xl p-4 md:p-8 bg-card text-center">
          <h2 className="font-semibold text-lg mb-2">Kontak Privasi</h2>
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
        <p>© 2026 JatuhTempo. All rights reserved.</p>
      </footer>
    </div>
  )
}
