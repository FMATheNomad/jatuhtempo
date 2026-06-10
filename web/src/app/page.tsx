'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { SummaryCards } from '@/components/dashboard/summary-cards'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { CreditCard, ArrowUpRight, BarChart3, Bell, Shield, ChevronRight } from 'lucide-react'

const statusVariant: Record<string, 'active' | 'paid' | 'late'> = {
  active: 'active', paid: 'paid', late: 'late',
}

function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="gradient-hero text-white">
        <nav className="flex items-center justify-between p-6 max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <img src="/assets/logo.webp" alt="JatuhTempo" className="h-8 w-auto" />
          </div>
          <div className="flex items-center gap-4 sm:gap-6 text-sm text-white/70">
            <a href="#features" className="hover:text-white transition-colors py-2">Fitur</a>
            <a href="/login" className="hover:text-white transition-colors py-2">Masuk</a>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-6 py-16 md:py-24">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="flex-1 animate-fade-in">
              <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-1.5 text-sm mb-8">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                AI-Powered Debt Management
              </div>
              <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6">
                Kelola Utang dengan{' '}
                <span className="bg-gradient-to-r from-emerald-300 to-cyan-300 text-transparent bg-clip-text">Cerdas</span>
              </h1>
              <p className="text-lg md:text-xl text-white/60 mb-10 max-w-xl leading-relaxed">
                OCR otomatis, pengingat cerdas, dan dashboard real-time. 
                Pantau semua tagihan dari Telegram atau Web.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <a href="/login">
                  <Button size="lg" className="bg-white text-primary hover:bg-white/90 w-full sm:w-auto">
                    Mulai Sekarang
                    <ArrowUpRight className="w-4 h-4 ml-2" />
                  </Button>
                </a>
                <a href="#features">
                  <Button size="lg" variant="outline" className="border-white/20 text-white bg-white/10 hover:bg-white/20 w-full sm:w-auto">
                    Pelajari Fitur
                  </Button>
                </a>
              </div>
            </div>
            <div className="flex-1 animate-fade-in">
              <img src="/assets/hero.webp" alt="Dashboard Preview" className="w-full rounded-2xl shadow-2xl" />
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 pb-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            {[
              ['💰', 'Rp1.2M+', 'Total utang terkelola'],
              ['📱', '1K+', 'Pengguna aktif'],
              ['🤖', '95%', 'Akurasi OCR'],
            ].map(([emoji, val, desc]) => (
              <div key={desc} className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10 flex items-center gap-4">
                <span className="text-2xl">{emoji}</span>
                <div>
                  <p className="font-semibold text-white">{val}</p>
                  <p className="text-white/50 text-xs">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6 max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Semua yang Anda Butuhkan</h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto">
            Dari screenshot hingga pelunasan — satu platform untuk semua tagihan Anda.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { icon: CreditCard, title: 'OCR Otomatis', desc: 'Foto tagihan, AI baca otomatis. Ekstrak jumlah, tanggal, dan platform dalam detik.' },
            { icon: Bell, title: 'Pengingat Cerdas', desc: 'Notifikasi H-7, H-3, H-1, dan hari H langsung ke Telegram. Tidak ada lagi telat bayar.' },
            { icon: BarChart3, title: 'Dashboard Real-time', desc: 'Pantau semua utang, riwayat pembayaran, dan rekap bulanan dari web atau bot.' },
            { icon: Shield, title: 'Multi-Platform', desc: 'Akses via Telegram, Web, dan segera WhatsApp. Data tetap sinkron di mana pun.' },
          ].map(({ icon: Icon, title, desc }) => (
            <Card key={title} className="card-hover">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-[#1a1a4e] flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-lg mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-6 text-center text-sm text-muted-foreground">
        <div className="flex items-center justify-center gap-4 mb-4">
          <a href="/faq" className="hover:text-foreground transition-colors">FAQ</a>
          <span className="text-border">•</span>
          <a href="/legal/terms" className="hover:text-foreground transition-colors">Terms</a>
          <span className="text-border">•</span>
          <a href="/legal/privacy" className="hover:text-foreground transition-colors">Privacy</a>
          <span className="text-border">•</span>
          <a href="/docs" className="hover:text-foreground transition-colors">Docs</a>
        </div>
        <p>© 2026 JatuhTempo. All rights reserved.</p>
      </footer>
    </div>
  )
}

// Dashboard
function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [debts, setDebts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ platform: '', amount: '', due_date: '', category: '', notes: '', installment_current: '', installment_total: '' })
  const [adding, setAdding] = useState(false)

  async function load() {
    try {
      const { getSummary, getDebts } = await import('@/lib/api')
      const [s, d] = await Promise.all([getSummary(), getDebts()])
      setSummary(s); setDebts(d)
    } catch { setError('Gagal memuat data. Coba refresh.') }
    setLoading(false)
  }

  useEffect(() => { load() }, [])

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
      })
      setForm({ platform: '', amount: '', due_date: '', category: '', notes: '', installment_current: '', installment_total: '' })
      load()
    } catch { setError('Gagal simpan utang') }
    setAdding(false)
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
              <p className="text-white/60 mb-8 max-w-md mx-auto">
                Masukkan informasi tagihan kamu di bawah. Nanti bisa upload screenshot juga.
              </p>

              <form onSubmit={handleAdd} className="max-w-lg mx-auto space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input value={form.platform} onChange={e => setForm({...form, platform: e.target.value})} placeholder="Nama platform" required className="h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" />
                  <input value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="Jumlah (Rp)" type="number" required className="h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input value={form.due_date} onChange={e => setForm({...form, due_date: e.target.value})} placeholder="Jatuh tempo (YYYY-MM-DD)" required className="h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" />
                  <input value={form.category} onChange={e => setForm({...form, category: e.target.value})} placeholder="Kategori (opsional)" className="h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input value={form.installment_current} onChange={e => setForm({...form, installment_current: e.target.value})} placeholder="Cicilan ke- (opsional)" type="number" className="h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" />
                  <input value={form.installment_total} onChange={e => setForm({...form, installment_total: e.target.value})} placeholder="Total cicilan (opsional)" type="number" className="h-12 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 px-4 text-sm" />
                </div>
                <button type="submit" disabled={adding} className="w-full h-12 rounded-xl bg-white text-primary font-semibold hover:bg-white/90 transition-colors disabled:opacity-50">
                  {adding ? 'Menyimpan...' : 'Tambah Utang'}
                </button>
              </form>
            </div>
          )}

          {summary && !empty && (
            <>
              <SummaryCards summary={summary} />

              {/* Quick add */}
              <Card>
                <CardHeader><CardTitle>Tambah Utang Cepat</CardTitle></CardHeader>
                <CardContent>
                  <form onSubmit={handleAdd} className="flex flex-col sm:flex-row gap-3 flex-wrap">
                    <input value={form.platform} onChange={e => setForm({...form, platform: e.target.value})} placeholder="Platform" className="flex-1 min-w-[120px] h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                    <input value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="Jumlah" type="number" className="w-full sm:w-28 h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                    <input value={form.due_date} onChange={e => setForm({...form, due_date: e.target.value})} placeholder="YYYY-MM-DD" className="w-full sm:w-32 h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                    <input value={form.installment_current} onChange={e => setForm({...form, installment_current: e.target.value})} placeholder="Cicilan ke-" type="number" className="w-full sm:w-24 h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                    <input value={form.installment_total} onChange={e => setForm({...form, installment_total: e.target.value})} placeholder="Total cicilan" type="number" className="w-full sm:w-24 h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                    <Button type="submit" disabled={adding} size="sm" className="sm:w-auto">Tambah</Button>
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
