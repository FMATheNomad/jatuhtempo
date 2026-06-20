'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { SummaryCards } from '@/components/dashboard/summary-cards'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  CreditCard, ArrowUpRight, BarChart3, Bell, Shield,
  ChevronRight, ChevronDown, Menu, X, Camera, Brain,
  CheckCircle2, Smartphone, ScanLine, Sparkles, Upload
} from 'lucide-react'
import type { DebtResponse, MonthlySummary } from '@/lib/api'

const statusVariant: Record<string, 'active' | 'paid' | 'late'> = {
  active: 'active', paid: 'paid', late: 'late',
}

const features = [
  { icon: Camera, title: 'OCR Otomatis', desc: 'Foto tagihan, AI baca otomatis. Ekstrak jumlah, tanggal, dan platform dalam detik.' },
  { icon: Bell, title: 'Pengingat Cerdas', desc: 'Notifikasi H-7, H-3, H-1, dan hari H langsung ke Telegram. Tidak ada lagi telat bayar.' },
  { icon: BarChart3, title: 'Dashboard Real-time', desc: 'Pantau semua utang, riwayat pembayaran, dan rekap bulanan dari web atau bot.' },
  { icon: Shield, title: 'Multi-Platform', desc: 'Akses via Telegram, Web, dan segera WhatsApp. Data tetap sinkron di mana pun.' },
  { icon: Brain, title: 'AI Learning', desc: 'Sistem belajar bunga dan pola dari setiap input user. Makin sering dipake, makin pinter.' },
  { icon: Smartphone, title: 'Bot Telegram', desc: 'Tambah utang pake bahasa sehari-hari. "Gua utang 2000 ke bahlul" — AI langsung paham.' },
]

const steps = [
  { icon: ScanLine, title: 'Foto atau Ketik', desc: 'Screenshot tagihan langsung terdeteksi. Atau cukup ketik pake bahasa sehari-hari di Telegram.' },
  { icon: Brain, title: 'AI Parsing Otomatis', desc: 'AI membaca platform, jumlah, tanggal jatuh tempo, bunga, dan cicilan — semua otomatis.' },
  { icon: CheckCircle2, title: 'Track & Bebas Utang', desc: 'Dapat pengingat otomatis, lihat progress, dan simulasi kapan kamu bakal bebas utang.' },
]

const faqs = [
  { q: 'Apa itu JatuhTempo?', a: 'JatuhTempo adalah asisten manajemen utang berbasis AI. Kamu bisa foto tagihan, AI baca otomatis, dapet pengingat, dan pantau semua utang dari Telegram atau Web.' },
  { q: 'Apakah data saya aman?', a: 'Ya. Semua data terenkripsi dan disimpan aman di database. Kami tidak punya akses ke rekening atau data finansial sensitif lainnya.' },
  { q: 'Bagaimana cara mulai?', a: 'Cukup buka @JatuhTempo_bot di Telegram, ketik /start, dan kirim screenshot tagihan pertama kamu. Atau langsung daftar di web.' },
  { q: 'Berapa biayanya?', a: 'Saat ini masih gratis untuk semua pengguna. Fitur premium akan datang untuk mendukung pengembangan.' },
  { q: 'Platform apa saja yang didukung?', a: 'Semua platform pinjaman dan paylater Indonesia: Kredivo, Akulaku, Shopee PayLater, GoPay Later, Bank, koperasi, dan lainnya.' },
  { q: 'Ada komunitasnya?', a: 'JatuhTempo mendukung Komunitas Bebas Utang (KOMBAT) by Guru Gembul — komunitas yang saling membantu bebas dari utang.' },
]

// Landing Page — dark theme (intentional: transitions to light dashboard after login)
function LandingPage() {
  const [mobileMenu, setMobileMenu] = useState(false)
  const [openFaq, setOpenFaq] = useState<number | null>(null)
  const [stats, setStats] = useState<{ total_users: number; total_amount?: number } | null>(null)

  useEffect(() => {
    fetch('/api/stats')
      .then(r => r.json())
      .then(d => setStats(d))
      .catch(() => setStats(null))
  }, [])

  const statItems = stats ? [
    ['📱', `${stats.total_users || 0}`, 'Pengguna aktif'],
    ['💰', `${stats.total_debts || 0}`, 'Total utang tercatat'],
    ['✅', `${stats.total_paid || 0}`, 'Utang lunas'],
  ] : null

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-gradient-to-b dark:from-[#0a0b1e] dark:via-[#0f1535] dark:to-[#0f1535]">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-slate-200 dark:border-white/10 bg-white/80 dark:bg-[#0a0b1e]/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <img src="/assets/logo.webp" alt="JatuhTempo" className="h-7 w-auto" />
            <span className="text-lg font-bold text-slate-900 dark:text-white">JatuhTempo</span>
          </div>
          <div className="hidden items-center gap-6 md:flex">
            <a href="#features" className="text-sm text-slate-500 dark:text-white/60 hover:text-slate-900 dark:hover:text-white transition-colors">Fitur</a>
            <a href="#how" className="text-sm text-slate-500 dark:text-white/60 hover:text-slate-900 dark:hover:text-white transition-colors">Cara Kerja</a>
            <a href="#faq" className="text-sm text-slate-500 dark:text-white/60 hover:text-slate-900 dark:hover:text-white transition-colors">FAQ</a>
          </div>
          <div className="hidden items-center gap-2 md:flex">
            <a href="/login" className="rounded-full border border-slate-300 dark:border-white/20 px-4 py-1.5 text-sm font-medium text-slate-700 dark:text-white/80 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors">
              Masuk
            </a>
            <a href="/login?mode=register" className="rounded-full bg-teal-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-teal-600 transition-colors">
              Mulai Gratis
            </a>
          </div>
          <button className="md:hidden text-slate-900 dark:text-white" onClick={() => setMobileMenu(!mobileMenu)}>
            {mobileMenu ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
        {mobileMenu && (
          <div className="flex flex-col gap-2 border-t border-slate-200 dark:border-white/10 px-4 py-3 md:hidden bg-white dark:bg-[#0a0b1e]">
            <a href="#features" className="text-sm py-1 text-slate-500 dark:text-white/60" onClick={() => setMobileMenu(false)}>Fitur</a>
            <a href="#how" className="text-sm py-1 text-slate-500 dark:text-white/60" onClick={() => setMobileMenu(false)}>Cara Kerja</a>
            <a href="#faq" className="text-sm py-1 text-slate-500 dark:text-white/60" onClick={() => setMobileMenu(false)}>FAQ</a>
            <div className="flex gap-2 pt-2">
              <a href="/login" className="flex-1 rounded-full border border-slate-300 dark:border-white/20 py-2 text-sm font-medium text-slate-700 dark:text-white/80 text-center">Masuk</a>
              <a href="/login?mode=register" className="flex-1 rounded-full bg-teal-500 py-2 text-sm font-medium text-white text-center">Mulai Gratis</a>
            </div>
          </div>
        )}
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-4 pt-16 pb-12 md:pt-24 md:pb-16">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-teal-500/10 border border-teal-500/20 px-3 py-1 text-xs font-medium text-teal-600 dark:text-teal-400">
              <Sparkles className="h-3 w-3" /> AI-Powered Debt Management
            </div>
            <h1 className="text-4xl font-bold leading-tight tracking-tight text-slate-900 dark:text-white md:text-5xl lg:text-6xl">
              Kelola Utang dengan{' '}
              <span className="bg-gradient-to-r from-teal-500 to-cyan-500 dark:from-teal-300 dark:to-cyan-300 bg-clip-text text-transparent">Cerdas</span>
            </h1>
            <p className="text-lg text-slate-500 dark:text-white/50 max-w-xl leading-relaxed">
              OCR otomatis, pengingat cerdas, dan dashboard real-time. 
              Pantau semua tagihan dari Telegram atau Web — cukup foto atau ketik.
            </p>
            <div className="flex flex-wrap gap-3">
              <a href="/login?mode=register">
                <Button size="lg" className="rounded-full bg-teal-500 hover:bg-teal-600 text-white px-8">
                  Mulai Sekarang <ArrowUpRight className="w-4 h-4 ml-1" />
                </Button>
              </a>
              <a href="#how">
                <Button size="lg" variant="outline" className="rounded-full border-slate-300 dark:border-white/30 text-slate-700 dark:text-white/80 hover:bg-slate-100 dark:hover:bg-white/10 bg-transparent px-8">
                  Cara Kerja
                </Button>
              </a>
            </div>
            <div className="flex items-center gap-6 pt-2">
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-white/60">
                <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400" />
                Gratis
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-white/60">
                <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400" />
                Telegram & Web
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-white/60">
                <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400" />
                No card required
              </div>
            </div>
          </div>
          <div className="flex justify-center">
            <img src="/assets/hero-image.png" alt="JatuhTempo Dashboard Preview" className="w-full max-w-lg rounded-2xl shadow-2xl shadow-black/20 dark:shadow-black/30" />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-6xl px-4 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {statItems ? statItems.map(([emoji, val, desc]) => (
            <div key={desc} className="bg-white dark:bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-slate-200 dark:border-white/10 flex items-center gap-4">
              <span className="text-2xl">{emoji}</span>
              <div>
                <p className="font-semibold text-slate-900 dark:text-white">{val}</p>
                <p className="text-slate-500 dark:text-white/60 text-xs">{desc}</p>
              </div>
            </div>
          )) : (
            <div className="col-span-3 text-center text-sm text-slate-400 dark:text-white/40 py-4">
              Data akan muncul setelah kamu mulai menggunakan JatuhTempo
            </div>
          )}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="border-t border-slate-200 dark:border-white/10 bg-slate-100/50 dark:bg-[#0f1535]/50 py-20">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Fitur Unggulan</h2>
            <p className="mt-2 text-slate-500 dark:text-white/60">Semua yang kamu butuh buat keluar dari utang</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => (
              <div key={i} className="group rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-6 transition-all hover:bg-slate-50 dark:hover:bg-white/10 hover:border-teal-500/30">
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-600 dark:text-teal-400">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="mb-2 font-semibold text-slate-900 dark:text-white">{f.title}</h3>
                <p className="text-sm text-slate-500 dark:text-white/60">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how" className="py-20">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Cara Kerja</h2>
            <p className="mt-2 text-slate-500 dark:text-white/60">Tiga langkah aja</p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            {steps.map((s, i) => (
              <div key={i} className="text-center">
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-teal-500/10 text-teal-600 dark:text-teal-400">
                  <s.icon className="h-6 w-6" />
                </div>
                <h3 className="mb-2 font-semibold text-slate-900 dark:text-white">{s.title}</h3>
                <p className="text-sm text-slate-500 dark:text-white/60">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="border-t border-slate-200 dark:border-white/10 bg-slate-100/50 dark:bg-[#0f1535]/50 py-20">
        <div className="mx-auto max-w-2xl px-4">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Pertanyaan Umum</h2>
          </div>
          <div className="space-y-2">
            {faqs.map((faq, i) => (
              <div key={i} className="rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="flex w-full items-center justify-between px-5 py-4 text-left text-sm font-medium text-slate-900 dark:text-white"
                >
                  {faq.q}
                  <ChevronDown className={`h-4 w-4 text-slate-400 dark:text-white/60 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                </button>
                {openFaq === i && (
                  <div className="border-t border-slate-200 dark:border-white/10 px-5 py-4 text-sm text-slate-500 dark:text-white/60">{faq.a}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust */}
      <section className="py-16">
        <div className="mx-auto max-w-4xl px-4 text-center">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-8">Data Kamu, Hak Kamu</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              { icon: Shield, title: 'Enkripsi Penuh', desc: 'Semua data terenkripsi. Kami tidak bisa membaca data kamu.' },
              { icon: CheckCircle2, title: 'No Bank Access', desc: 'Kami tidak terhubung ke rekening atau dompet digital kamu.' },
              { icon: Brain, title: 'AI, Tapi Aman', desc: 'AI hanya baca teks dari screenshot. Tidak ada data yang bocor.' },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-6">
                <Icon className="h-8 w-8 mx-auto mb-3 text-teal-600 dark:text-teal-400" />
                <h3 className="font-semibold text-slate-900 dark:text-white mb-1">{title}</h3>
                <p className="text-sm text-slate-500 dark:text-white/60">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="border-t border-slate-200 dark:border-white/10 py-20">
        <div className="mx-auto max-w-2xl px-4 text-center">
          <h2 className="mb-4 text-3xl font-bold text-slate-900 dark:text-white">Siap Bebas Utang?</h2>
          <p className="mb-8 text-slate-500 dark:text-white/60">Gratis. 1 klik. Langsung jalan.</p>
          <a href="/login?mode=register">
            <Button size="lg" className="rounded-full bg-teal-500 hover:bg-teal-600 text-white px-10 py-6 text-base">
              Mulai Sekarang <ArrowUpRight className="w-4 h-4 ml-2" />
            </Button>
          </a>
          <p className="mt-4 text-xs text-slate-400 dark:text-white/50">Didukung oleh FMA Software Labs & Komunitas Bebas Utang (KOMBAT)</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-white/10 py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-4 text-sm text-slate-500 dark:text-white/60 md:flex-row md:justify-between">
          <div className="flex items-center gap-2">
            <img src="/assets/logo.webp" alt="" className="h-5 w-auto" />
            JatuhTempo
          </div>
          <div className="flex items-center gap-4">
            <a href="/faq" className="hover:text-slate-900 dark:hover:text-white/70 transition-colors">FAQ</a>
            <a href="/legal/terms" className="hover:text-slate-900 dark:hover:text-white/70 transition-colors">Terms</a>
            <a href="/legal/privacy" className="hover:text-slate-900 dark:hover:text-white/70 transition-colors">Privacy</a>
            <a href="/docs" className="hover:text-slate-900 dark:hover:text-white/70 transition-colors">Docs</a>
          </div>
          <p>© {new Date().getFullYear()} FMA Software Labs. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

// Dashboard
function DashboardPage() {
  const [summary, setSummary] = useState<MonthlySummary | null>(null)
  const [debts, setDebts] = useState<DebtResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ platform: '', amount: '', due_date: '', category: '', notes: '', installment_current: '', installment_total: '', interest_rate: '', interest_type: '' })
  const [adding, setAdding] = useState(false)
  const [rateSuggestion, setRateSuggestion] = useState<{ rate: number; type: string } | null>(null)

  async function load() {
    try {
      const { getSummary, getDebts } = await import('@/lib/api')
      const [s, d] = await Promise.all([getSummary(), getDebts()])
      setSummary(s); setDebts(d)
    } catch { setError('Gagal memuat data. Coba refresh.') }
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  async function handlePlatformChange(platform: string) {
    setForm({...form, platform, interest_rate: '', interest_type: '' })
    setRateSuggestion(null)
    if (!platform) return
    const { getPlatformRate } = await import('@/lib/api')
    const rate = await getPlatformRate(platform)
    if (rate && rate.confidence > 0.3) {
      setRateSuggestion({ rate: rate.avg_rate, type: rate.common_type || 'monthly' })
      setForm(prev => ({ ...prev, platform, interest_rate: String(rate.avg_rate), interest_type: rate.common_type || 'monthly' }))
    }
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!form.platform || !form.amount || !form.due_date) return
    setAdding(true)
    try {
      const { createDebt } = await import('@/lib/api')
      await createDebt({
        platform: form.platform, amount: parseInt(form.amount) || 0,
        due_date: form.due_date, category: form.category || null, notes: form.notes || null,
        installment_current: form.installment_current ? parseInt(form.installment_current) : null,
        installment_total: form.installment_total ? parseInt(form.installment_total) : null,
        interest_rate: form.interest_rate ? parseFloat(form.interest_rate) : null,
        interest_type: form.interest_type || null,
      })
      setForm({ platform: '', amount: '', due_date: '', category: '', notes: '', installment_current: '', installment_total: '', interest_rate: '', interest_type: '' })
      load()
    } catch { setError('Gagal simpan utang') }
    setAdding(false)
  }

  function AddDebtForm({ variant, className }: { variant: 'hero' | 'card'; className?: string }) {
    const isHero = variant === 'hero'
    return (
      <form onSubmit={handleAdd} className={className}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input value={form.platform} onChange={e => handlePlatformChange(e.target.value)} placeholder={isHero ? "Nama platform" : "Platform"} required className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"} />
          <input value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="Jumlah (Rp)" type="number" required className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input value={form.due_date} onChange={e => setForm({...form, due_date: e.target.value})} placeholder="Jatuh tempo (YYYY-MM-DD)" required className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"} />
          <input value={form.category} onChange={e => setForm({...form, category: e.target.value})} placeholder="Kategori (opsional)" className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input value={form.installment_current} onChange={e => setForm({...form, installment_current: e.target.value})} placeholder="Cicilan ke- (opsional)" type="number" className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"} />
          <input value={form.installment_total} onChange={e => setForm({...form, installment_total: e.target.value})} placeholder="Total cicilan (opsional)" type="number" className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input value={form.interest_rate} onChange={e => setForm({...form, interest_rate: e.target.value})} placeholder="Bunga (%), opsional" type="number" step="0.1" className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"} />
          <select value={form.interest_type} onChange={e => setForm({...form, interest_type: e.target.value})} className={isHero ? "h-12 rounded-xl bg-white/10 border border-white/20 text-white px-4 text-sm" : "h-12 rounded-xl border border-input bg-background px-4 text-sm"}>
            <option value="">Tipe Bunga (opsional)</option>
            <option value="daily">Harian</option>
            <option value="monthly">Bulanan</option>
            <option value="yearly">Tahunan</option>
            <option value="flat">Flat</option>
          </select>
        </div>
        {rateSuggestion && (
          <div className={isHero ? "text-xs text-emerald-300 font-medium" : "text-xs text-accent font-medium"}>
            💡 Saran: bunga {rateSuggestion.rate}%/{rateSuggestion.type === 'monthly' ? 'bln' : rateSuggestion.type === 'daily' ? 'hari' : rateSuggestion.type === 'yearly' ? 'thn' : rateSuggestion.type}
          </div>
        )}
        <button type="submit" disabled={adding} className={isHero
          ? "w-full h-12 rounded-xl bg-white text-primary font-semibold hover:bg-white/90 transition-colors disabled:opacity-50"
          : "w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
        }>
          {adding ? 'Menyimpan...' : 'Tambah Utang'}
        </button>
      </form>
    )
  }

  const empty = !loading && debts.length === 0

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold">Dashboard</h1>
            <div className="flex items-center gap-3">
              <a href="/docs" className="text-xs text-muted-foreground hover:text-foreground transition-colors hidden sm:inline-flex items-center gap-1">
                Bantuan
              </a>
              <MobileNav />
            </div>
          </div>
        </header>

        <div className="p-4 lg:p-8 space-y-6 animate-fade-in">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">{error}</div>
          )}

          {/* Empty state hero */}
          {empty && !loading && (
            <div className="bg-gradient-to-br from-primary to-[#1a1a4e] rounded-2xl p-8 text-white text-center">
              <CreditCard className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <h2 className="text-2xl font-bold mb-2">Catat Utang Pertama Kamu</h2>
              <p className="text-white/60 mb-6 max-w-md mx-auto">
                Masukkan informasi tagihan di bawah. Atau upload screenshot — AI baca otomatis.
              </p>

              {/* Quick tutorial */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-xl mx-auto mb-8 text-left">
                {[
                  { icon: Upload, title: "1. Upload Screenshot", desc: "Foto tagihan kamu, AI ekstrak otomatis" },
                  { icon: CreditCard, title: "2. Isi Manual", desc: "Atau ketik manual pakai form di bawah" },
                  { icon: Bell, title: "3. Dapat Reminder", desc: "Notifikasi H-7, H-3, H-1, dan hari H" },
                ].map(({ icon: Icon, title, desc }) => (
                  <div key={title} className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                    <Icon className="w-6 h-6 text-teal-300 mb-2" />
                    <h3 className="font-semibold text-sm mb-1">{title}</h3>
                    <p className="text-xs text-white/60">{desc}</p>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-center mb-6">
                <a href="https://t.me/JatuhTempo_bot" target="_blank" className="inline-flex items-center gap-2 text-xs text-white/70 hover:text-white bg-white/10 hover:bg-white/20 px-4 py-2 rounded-full transition-all">
                  🤖 Buka Bot Telegram
                </a>
              </div>

              <AddDebtForm variant="hero" className="max-w-lg mx-auto space-y-3" />
            </div>
          )}

          {summary && !empty && (
            <>
              <SummaryCards summary={summary} />

              {/* Quick add */}
              <Card>
                <CardHeader><CardTitle>Tambah Utang Cepat</CardTitle></CardHeader>
                <CardContent>
                  <form onSubmit={handleAdd} className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Platform</label>
                        <input value={form.platform} onChange={e => handlePlatformChange(e.target.value)} placeholder="Kredivo, Akulaku..." required className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                      </div>
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Jumlah (Rp)</label>
                        <input value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="350000" type="number" required className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                      </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Jatuh Tempo</label>
                        <input value={form.due_date} onChange={e => setForm({...form, due_date: e.target.value})} placeholder="2026-07-15" required className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                      </div>
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Kategori</label>
                        <input value={form.category} onChange={e => setForm({...form, category: e.target.value})} placeholder="paylater, pinjol, kredit..." className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Cicilan ke-</label>
                        <input value={form.installment_current} onChange={e => setForm({...form, installment_current: e.target.value})} placeholder="3" type="number" className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                      </div>
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Total Cicilan</label>
                        <input value={form.installment_total} onChange={e => setForm({...form, installment_total: e.target.value})} placeholder="12" type="number" className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                      </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Bunga (%)</label>
                        <input value={form.interest_rate} onChange={e => setForm({...form, interest_rate: e.target.value})} placeholder="2.5" type="number" step="0.1" className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                      </div>
                      <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-muted-foreground">Tipe Bunga</label>
                        <select value={form.interest_type} onChange={e => setForm({...form, interest_type: e.target.value})} className="h-10 rounded-lg border border-input bg-background px-3 text-sm">
                          <option value="">—</option>
                          <option value="monthly">Bulanan</option>
                          <option value="daily">Harian</option>
                          <option value="yearly">Tahunan</option>
                          <option value="flat">Flat</option>
                        </select>
                      </div>
                    </div>
                    {rateSuggestion && (
                      <div className="text-xs text-accent font-medium bg-accent/5 border border-accent/20 rounded-lg px-3 py-2">
                        💡 Saran bunga {rateSuggestion.rate}%/{rateSuggestion.type === 'monthly' ? 'bln' : rateSuggestion.type === 'daily' ? 'hari' : rateSuggestion.type === 'yearly' ? 'thn' : rateSuggestion.type}
                      </div>
                    )}
                    <Button type="submit" disabled={adding} className="w-full">Tambah Utang</Button>
                  </form>
                </CardContent>
              </Card>

              {/* Recent debts */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Utang Terbaru</CardTitle>
                  <a href="/debts" className="text-sm text-accent hover:underline flex items-center gap-1">Lihat semua <ChevronRight className="w-3 h-3" /></a>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {debts.slice(0, 5).map((d: any) => (
                      <div key={d.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/50 transition-colors">
                        <div className="flex items-center gap-3">
                          <Badge variant={statusVariant[d.status] || 'default'}>
                            {d.status === 'active' ? '🟡' : d.status === 'paid' ? '✅' : '🔴'}
                          </Badge>
                          <div>
                            <p className="font-medium text-sm">{d.platform}</p>
                            <p className="text-xs text-muted-foreground">Jatuh tempo {d.due_date}</p>
                          </div>
                        </div>
                        <p className="font-semibold">Rp{d.amount.toLocaleString('id-ID')}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default function Home() {
  const [authed, setAuthed] = useState<boolean | null>(null)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('session_token')
    setAuthed(!!token)
  }, [])

  if (authed === null) return null

  if (!authed) return <LandingPage />
  return <DashboardPage />
}