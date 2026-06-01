'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Smartphone, LogOut } from 'lucide-react'

export default function SettingsPage() {
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
                <p className="text-sm text-muted-foreground">Telegram ID</p>
                <p className="font-medium">{user?.telegram_id || '-'}</p>
              </div>
            </CardContent>
          </Card>

          {/* WhatsApp Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-accent" />
                <div>
                  <CardTitle>WhatsApp</CardTitle>
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
                  className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
              <Button onClick={handleSave} className="w-full sm:w-auto">
                {saved ? '✓ Tersimpan' : 'Simpan'}
              </Button>
            </CardContent>
          </Card>

          {/* Logout */}
          <button
            onClick={() => { localStorage.removeItem('session_token'); window.location.href = '/' }}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-destructive transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Keluar dari semua perangkat
          </button>
        </div>
      </main>
    </div>
  )
}
