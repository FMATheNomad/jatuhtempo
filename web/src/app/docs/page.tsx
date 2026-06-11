import Link from 'next/link'
import type { Metadata } from 'next'
import { BookOpen, MessageCircle, Camera, ArrowUpRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Dokumentasi — JatuhTempo',
  description: 'Panduan lengkap menggunakan JatuhTempo',
}

const docCards = [
  {
    icon: BookOpen,
    title: 'Panduan Memulai',
    desc: 'Buat akun, tambah utang pertama, hubungkan Telegram, dan atur pengingat.',
    link: '/docs/getting-started',
    gradient: 'from-primary to-[#1a1a4e]',
  },
  {
    icon: MessageCircle,
    title: 'Bot Telegram',
    desc: 'Kelola utang langsung dari Telegram. Semua perintah dan cara pakai.',
    link: '/docs/telegram-bot',
    gradient: 'from-blue-600 to-blue-800',
  },
  {
    icon: Camera,
    title: 'Panduan OCR',
    desc: 'Cara upload screenshot tagihan dan optimasi hasil bacaan AI.',
    link: '/docs/ocr-guide',
    gradient: 'from-emerald-600 to-teal-700',
  },
]

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="gradient-hero text-white">
        <div className="max-w-3xl mx-auto px-6 py-16 md:py-24 text-center">
          <h1 className="text-3xl md:text-5xl font-bold mb-4 animate-fade-in">
            Dokumentasi
          </h1>
          <p className="text-white/60 text-lg max-w-lg mx-auto animate-fade-in">
            Semua yang perlu kamu tahu untuk memaksimalkan JatuhTempo
          </p>
        </div>
      </section>

      {/* Cards */}
      <div className="max-w-5xl mx-auto px-4 lg:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {docCards.map(({ icon: Icon, title, desc, link, gradient }) => (
            <Link
              key={title}
              href={link}
              className="group border border-border rounded-2xl p-6 bg-card card-hover block"
            >
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-4`}
              >
                <Icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-lg mb-2 group-hover:text-accent transition-colors flex items-center gap-2">
                {title}
                <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
            </Link>
          ))}
        </div>

        {/* Quick links */}
        <div className="mt-12 border border-border rounded-2xl p-4 md:p-8 bg-card">
          <h2 className="font-semibold text-lg mb-4">Markdown Source Files</h2>
          <p className="text-sm text-muted-foreground mb-4">
            File dokumentasi juga tersedia dalam format markdown untuk referensi cepat:
          </p>
          <ul className="space-y-2 text-sm">
            {[
              ['Panduan Memulai', '/content/docs/getting-started.md'],
              ['Bot Telegram', '/content/docs/telegram-bot.md'],
              ['Panduan OCR', '/content/docs/ocr-guide.md'],
              ['FAQ', '/content/faq.md'],
              ['Syarat & Ketentuan', '/content/terms.md'],
              ['Kebijakan Privasi', '/content/privacy.md'],
            ].map(([label, path]) => (
              <li key={label}>
                <a
                  href={path}
                  target="_blank"
                  className="text-accent hover:underline inline-flex items-center gap-1"
                >
                  {label}
                  <ArrowUpRight className="w-3 h-3" />
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Still need help */}
        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground">
            Masih butuh bantuan?{' '}
            <a href="mailto:support@jatuhtempo.app" className="text-accent hover:underline">
              Hubungi support
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
