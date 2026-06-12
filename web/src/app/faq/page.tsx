'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ChevronDown, ChevronUp, Search, ArrowLeft } from 'lucide-react'

interface FAQItem {
  q: string
  a: string
}

const categories: { title: string; items: FAQItem[] }[] = [
  {
    title: 'Akun & Tagihan',
    items: [
      {
        q: 'Bagaimana cara mendaftar?',
        a: 'Kunjungi halaman Login di web, pilih "Daftar", lalu masukkan nama, email, dan password. Setelah itu, kamu bisa langsung menggunakan dashboard.',
      },
      {
        q: 'Apakah JatuhTempo gratis?',
        a: 'Ya! Kamu bisa menggunakan JatuhTempo secara gratis untuk mencatat hingga 10 utang aktif. Untuk fitur unlimited (OCR tanpa batas, pengingat prioritas, dan ekspor data), tersedia langganan Pro.',
      },
      {
        q: 'Bagaimana cara berlangganan Pro?',
        a: 'Masuk ke menu Pengaturan → Langganan, lalu klik "Upgrade ke Pro". Kamu akan diarahkan ke halaman pembayaran.',
      },
      {
        q: 'Bisakah saya menghapus akun?',
        a: 'Saat ini belum ada fitur hapus akun mandiri. Hubungi kami melalui email fmasoftwarelabs@gmail.com untuk bantuan.',
      },
    ],
  },
  {
    title: 'Teknis',
    items: [
      {
        q: 'Bagaimana cara menambahkan utang?',
        a: 'Ada dua cara. Manual: di dashboard, isi form "Tambah Utang Cepat" dengan nama platform, jumlah, dan tanggal jatuh tempo. OCR: upload screenshot tagihan, dan AI akan membaca otomatis.',
      },
      {
        q: 'Bagaimana cara menggunakan OCR?',
        a: 'Di dashboard, klik tombol upload gambar, pilih screenshot tagihan kamu, dan sistem akan mengekstrak informasi secara otomatis. Pastikan gambar jelas dan terbaca.',
      },
      {
        q: 'Data saya aman?',
        a: 'Ya. Semua data terenkripsi dan disimpan dengan aman. Kami tidak membagikan data kamu ke pihak ketiga. Lihat kebijakan privasi kami untuk detail lebih lanjut.',
      },
      {
        q: 'Bisakah saya akses dari Telegram?',
        a: 'Tentu! Cari @JatuhTempo_bot di Telegram, lalu login dengan mengirim perintah /login. Semua data akan sinkron antara web dan Telegram.',
      },
    ],
  },
  {
    title: 'Pembayaran',
    items: [
      {
        q: 'Metode pembayaran apa yang didukung?',
        a: 'Kami mendukung transfer bank (BCA, Mandiri, BRI, BNI) dan e-wallet (GoPay, OVO, Dana).',
      },
      {
        q: 'Apakah ada garansi uang kembali?',
        a: 'Untuk pengguna Pro, kami memberikan garansi uang kembali dalam 7 hari pertama jika kamu tidak puas dengan layanan.',
      },
      {
        q: 'Bagaimana cara membatalkan langganan?',
        a: 'Kamu bisa membatalkan kapan saja dari menu Pengaturan → Langganan. Akses Pro tetap aktif sampai akhir periode pembayaran.',
      },
    ],
  },
]

function FAQCategory({ title, items }: { title: string; items: FAQItem[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">{title}</h2>
      <div className="space-y-2">
        {items.map((item, i) => {
          const isOpen = openIndex === i
          return (
            <div
              key={i}
              className="border border-border rounded-xl overflow-hidden bg-card"
            >
              <button
                onClick={() => setOpenIndex(isOpen ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left text-sm font-medium hover:bg-secondary/50 transition-colors"
              >
                <span>{item.q}</span>
                {isOpen ? (
                  <ChevronUp className="w-4 h-4 text-muted-foreground shrink-0 ml-2" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0 ml-2" />
                )}
              </button>
              {isOpen && (
                <div className="px-4 pb-4 text-sm text-muted-foreground leading-relaxed animate-fade-in">
                  {item.a}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function FAQPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 pt-6">
        <Link href="/" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Kembali ke Beranda
        </Link>
      </div>
      {/* Hero */}
      <section className="gradient-hero text-white">
        <div className="max-w-3xl mx-auto px-6 py-16 md:py-24 text-center">
          <h1 className="text-3xl md:text-5xl font-bold mb-4 animate-fade-in">
            FAQ
          </h1>
          <p className="text-white/60 text-lg max-w-lg mx-auto animate-fade-in">
            Pertanyaan yang sering diajukan tentang JatuhTempo
          </p>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-4 lg:px-6 py-12 space-y-10 animate-fade-in">
        {categories.map((cat) => (
          <FAQCategory key={cat.title} title={cat.title} items={cat.items} />
        ))}

        {/* Still have questions */}
        <div className="border border-border rounded-2xl p-4 md:p-8 text-center bg-card">
          <h3 className="font-semibold text-lg mb-2">Masih ada pertanyaan?</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Tim kami siap membantu. Hubungi kami di email atau Telegram.
          </p>
          <a
            href="mailto:fmasoftwarelabs@gmail.com"
            className="inline-flex items-center justify-center h-10 px-6 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Hubungi Support
          </a>
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
