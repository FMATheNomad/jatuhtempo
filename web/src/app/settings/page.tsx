'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Smartphone, LogOut, Sparkles, MessageCircle, Sun, Moon, Monitor, Trash2, Pencil, X } from 'lucide-react'
import { useTheme } from '@/components/theme-provider'

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [phone, setPhone] = useState('')
  const [saved, setSaved] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [editingName, setEditingName] = useState(false)
  const [editNama, setEditNama] = useState('')

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
                <p className="text-sm text-muted-foreground mb-1">Nama</p>
                <div className="flex gap-2">
                  <input
                    value={editingName ? editNama : user?.nama || ''}
                    onChange={e => setEditNama(e.target.value)}
                    disabled={!editingName}
                    className="flex-1 h-10 rounded-lg border border-input bg-background px-3 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                  {!editingName ? (
                    <button onClick={() => { setEditNama(user?.nama || ''); setEditingName(true) }} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-secondary transition-colors">
                      <Pencil className="w-4 h-4 text-muted-foreground" />
                    </button>
                  ) : (
                    <div className="flex gap-1">
                      <button onClick={async () => {
                        try {
                          const token = localStorage.getItem('session_token')
                          const res = await fetch('/api/auth/profile', {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                            body: JSON.stringify({ nama: editNama }),
                          })
                          if (!res.ok) throw new Error()
                          setUser({ ...user, nama: editNama })
                          setEditingName(false)
                        } catch { setError('Gagal menyimpan') }
                      }} className="min-h-[44px] px-3 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">Simpan</button>
                      <button onClick={() => setEditingName(false)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-secondary transition-colors"><X className="w-4 h-4" /></button>
                    </div>
                  )}
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{user?.email || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Telegram</p>
                <p className="font-medium">{user?.telegram_id ? `Terhubung (ID: ${user.telegram_id})` : 'Belum terhubung'}</p>
              </div>
              <div className="pt-2">
                <a href="/reset-password" className="text-sm text-accent hover:underline">Ganti Password</a>
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
                  <CardDescription>
                    {user?.subscription_status === 'pro' ? 'Kamu sedang menikmati fitur Pro' : 'Upgrade untuk fitur tambahan'}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {user?.subscription_status === 'pro' ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {[
                      ['✅ Catat utang', 'Unlimited'],
                      ['✅ OCR', 'Unlimited'],
                      ['✅ Export CSV/PDF', 'Aktif'],
                      ['✅ Debt Health Score', 'Aktif'],
                      ['✅ Prioritas AI', 'Aktif'],
                    ].map(([f, v]) => (
                      <div key={f} className="flex items-center gap-2 p-2 rounded-lg bg-secondary/50">
                        <span className="text-xs">{f}</span>
                        <span className="text-xs font-medium ml-auto">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {[
                      ['Catat utang', '✅ Unlimited'],
                      ['OCR / bulan', '5x gratis'],
                      ['Reminder Telegram', '✅'],
                      ['Export CSV/PDF', '🔒 Pro'],
                      ['Debt Health Score', '🔒 Pro'],
                      ['Prioritas AI', '🔒 Pro'],
                    ].map(([f, v]) => (
                      <div key={f} className="flex items-center gap-2 p-2 rounded-lg bg-secondary/50">
                        <span className="text-xs">{f}</span>
                        <span className="text-xs font-medium ml-auto">{v}</span>
                      </div>
                    ))}
                  </div>
                  <Button
                    variant="accent"
                    onClick={async () => {
                      try {
                        const { getCheckoutUrl } = await import('@/lib/api')
                        const { url } = await getCheckoutUrl()
                        if (url) window.location.href = url
                      } catch { alert('Gagal memuat checkout.') }
                    }}
                    className="w-full"
                  >
                    Upgrade ke Pro
                  </Button>
                </div>
              )}
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
              onClick={async () => {
                const token = localStorage.getItem('session_token')
                if (token) await fetch('/api/auth/logout', { method: 'POST', headers: { Authorization: `Bearer ${token}` } }).catch(() => {})
                localStorage.removeItem('session_token')
                window.location.href = '/'
              }}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-destructive transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Keluar
            </button>
            <p className="text-xs text-muted-foreground/60 pl-6">Token akan dinonaktifkan. Perlu login ulang di semua perangkat.</p>
          </div>

          {/* Delete Account */}
          <div className="border border-red-200 dark:border-red-900/50 rounded-xl p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Trash2 className="w-5 h-5 text-red-500" />
              <div>
                <p className="font-semibold text-sm text-red-700 dark:text-red-400">Hapus Akun</p>
                <p className="text-xs text-muted-foreground">Semua data utang, pembayaran, dan pengingat akan dihapus permanen.</p>
              </div>
            </div>
            {!deleteConfirm ? (
              <button onClick={() => setDeleteConfirm(true)} className="min-h-[44px] px-4 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition-colors">
                Hapus Akun Saya
              </button>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-red-600 font-medium">Apakah kamu yakin? Tindakan ini tidak bisa dibatalkan.</p>
                {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}
                <div className="flex gap-2">
                  <button
                    onClick={async () => {
                      setDeleting(true); setDeleteError(null)
                      try {
                        const token = localStorage.getItem('session_token')
                        const res = await fetch('/api/auth/delete-account', { method: 'POST', headers: { Authorization: `Bearer ${token}` } })
                        if (!res.ok) throw new Error('Gagal menghapus akun')
                        localStorage.removeItem('session_token')
                        window.location.href = '/'
                      } catch (e: any) { setDeleteError(e.message); setDeleting(false) }
                    }}
                    disabled={deleting}
                    className="min-h-[44px] px-4 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 disabled:opacity-50 transition-colors"
                  >
                    {deleting ? 'Menghapus...' : 'Ya, Hapus Akun Saya'}
                  </button>
                  <button onClick={() => { setDeleteConfirm(false); setDeleteError(null) }} className="min-h-[44px] px-4 rounded-lg border border-input bg-background text-sm font-medium hover:bg-secondary transition-colors">
                    Batal
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
