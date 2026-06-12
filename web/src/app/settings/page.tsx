'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Smartphone, LogOut, Sparkles, MessageCircle, Sun, Moon, Monitor } from 'lucide-react'
import { useTheme } from '@/components/theme-provider'

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [phone, setPhone] = useState('')
  const [saved, setSaved] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const { getUser } = await import('@/lib/api')
        const u = await getUser()
        setUser(u)
        setPhone(u.phone_number || '')
      } catch { setError('Gagal memuat profil.') }
    }
    load()
  }, [])

  async function handleSave() {
    try {
      const { updatePhone } = await import('@/lib/api')
      await updatePhone(phone)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch { /* ignore */ }
  }

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold">Pengaturan</h1>
            <MobileNav />
          </div>
        </header>

        <div className="p-4 lg:p-8 max-w-2xl space-y-6 animate-fade-in">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">{error}</div>
          )}
          {/* Profile Card */}
          <Card>
            <CardHeader>
              <CardTitle>Profil</CardTitle>
              <CardDescription>Informasi akun Anda</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Nama</p>
                <p className="font-medium">{user?.nama || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{user?.email || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Telegram</p>
                <p className="font-medium">{user?.telegram_id ? `Terhubung (ID: ${user.telegram_id})` : 'Belum terhubung'}</p>
              </div>
            </CardContent>
          </Card>

          {/* Link Telegram Card */}
          {user && !user.telegram_id && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <MessageCircle className="w-5 h-5 text-blue-500" />
                  <div>
                    <CardTitle>Tautkan Telegram</CardTitle>
                    <CardDescription>Hubungkan akun Telegram untuk notifikasi</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  Buka bot Telegram dan ketik /login, lalu klik link yang dikirim.
                </p>
                <a
                  href={`https://t.me/JatuhTempo_bot`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center min-h-[44px] px-4 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90"
                >
                  Buka Bot Telegram
                </a>
              </CardContent>
            </Card>
          )}

          {/* Subscription Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <div>
                  <CardTitle>Langganan</CardTitle>
                  <CardDescription>Upgrade untuk fitur unlimited</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button
                variant="accent"
                onClick={async () => {
                  try {
                    const { getCheckoutUrl } = await import('@/lib/api')
                    const { url } = await getCheckoutUrl()
                    if (url) window.location.href = url
                  } catch { alert('Gagal memuat checkout.') }
                }}
              >
                Upgrade ke Pro
              </Button>
            </CardContent>
          </Card>

          {/* WhatsApp Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-accent" />
                <div>
                  <CardTitle>WhatsApp <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">Segera hadir</span></CardTitle>
                  <CardDescription>Hubungkan nomor WhatsApp untuk pengingat via WA</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm text-muted-foreground block mb-1.5">Nomor WhatsApp</label>
                <input
                  value={phone}
                  onChange={e => setPhone(e.target.value)}
                  placeholder="+628123456789"
                  className="w-full min-h-[44px] rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <Button onClick={handleSave} className="w-full sm:w-auto">
                {saved ? '✓ Tersimpan' : 'Simpan'}
              </Button>
            </CardContent>
          </Card>

          {/* Theme */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                {theme === 'light' ? <Sun className="w-5 h-5 text-amber-500" /> : theme === 'dark' ? <Moon className="w-5 h-5 text-indigo-400" /> : <Monitor className="w-5 h-5 text-accent" />}
                <div>
                  <CardTitle>Tampilan</CardTitle>
                  <CardDescription>Atur tema sesuai preferensi</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                {(['light', 'dark', 'system'] as const).map(t => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={`flex-1 min-h-[44px] rounded-lg border text-sm font-medium transition-all ${
                      theme === t
                        ? 'border-accent bg-accent/10 text-accent shadow-sm'
                        : 'border-input bg-background text-muted-foreground hover:bg-secondary'
                    }`}
                  >
                    {t === 'light' ? <><Sun className="w-4 h-4 mx-auto mb-1" /> Terang</> : t === 'dark' ? <><Moon className="w-4 h-4 mx-auto mb-1" /> Gelap</> : <><Monitor className="w-4 h-4 mx-auto mb-1" /> Sistem</>}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Logout */}
          <div className="space-y-2">
            <button
              onClick={() => { localStorage.removeItem('session_token'); window.location.href = '/' }}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-destructive transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Keluar (browser ini saja)
            </button>
            <p className="text-xs text-muted-foreground/60 pl-6">Token akan tetap valid di perangkat lain sampai kedaluwarsa.</p>
          </div>
        </div>
      </main>
    </div>
  )
}
