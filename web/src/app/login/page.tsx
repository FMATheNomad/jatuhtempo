'use client'

import { Suspense, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useEffect } from 'react'

const BOT_USERNAME = '@JatuhTempo_bot'

function LoginContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get('token')
  const [status, setStatus] = useState(token ? 'Memproses...' : '')
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nama, setNama] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!token) return
    fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })
      .then(res => { if (!res.ok) throw new Error(); return res.json() })
      .then(data => {
        localStorage.setItem('session_token', data.session_token)
        setStatus('Berhasil! Mengarahkan...')
        setTimeout(() => router.push('/'), 1000)
      })
      .catch(() => setStatus('Token tidak valid atau kadaluarsa.'))
  }, [token, router])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true); setError('')
    const endpoint = mode === 'login' ? '/api/auth/login-web' : '/api/auth/register'
    const body = mode === 'register' ? { email, password, nama } : { email, password }
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Gagal')
      localStorage.setItem('session_token', data.session_token)
      router.push('/')
    } catch (e: any) { setError(e.message) }
    setLoading(false)
  }

  if (token) {
    return (
      <div className="min-h-screen gradient-hero flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 text-center">
          <img src="/assets/logo.webp" alt="JatuhTempo" className="h-12 mx-auto mb-6" />
          <p className="text-muted-foreground">{status}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen gradient-hero flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4 animate-fade-in">
        <img src="/assets/logo.webp" alt="JatuhTempo" className="h-12 mx-auto mb-6" />

        <h1 className="text-xl font-bold mb-1">{mode === 'login' ? 'Masuk' : 'Daftar'}</h1>
        <p className="text-sm text-muted-foreground mb-6">
          {mode === 'login' ? 'Sudah punya akun? Masuk dengan email.' : 'Buat akun baru untuk mulai.'}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="text-sm font-medium mb-1 block">Nama</label>
              <input value={nama} onChange={e => setNama(e.target.value)} className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm" />
            </div>
          )}
          <div>
            <label className="text-sm font-medium mb-1 block">Email</label>
            <input value={email} onChange={e => setEmail(e.target.value)} type="email" required className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm" />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Password</label>
            <input value={password} onChange={e => setPassword(e.target.value)} type="password" required minLength={6} className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm" />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button type="submit" disabled={loading} className="w-full h-10 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 disabled:opacity-50">
            {loading ? 'Memproses...' : mode === 'login' ? 'Masuk' : 'Daftar'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }} className="text-sm text-accent hover:underline">
            {mode === 'login' ? 'Belum punya akun? Daftar' : 'Sudah punya akun? Masuk'}
          </button>
        </div>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t" /></div>
          <div className="relative flex justify-center text-xs text-muted-foreground"><span className="bg-white px-2">atau</span></div>
        </div>

        <a href={`https://t.me/${BOT_USERNAME.replace('@', '')}`} target="_blank" className="flex items-center justify-center gap-2 w-full h-10 rounded-lg border border-input bg-background text-sm font-medium hover:bg-secondary">
          Login dengan Telegram
        </a>

        <p className="text-xs text-muted-foreground text-center mt-4">
          Setelah login, tautkan Telegram di menu Pengaturan.
        </p>

        <div className="mt-6 pt-4 border-t border-border text-xs text-muted-foreground flex items-center justify-center gap-2">
          <a href="/faq" className="hover:text-foreground transition-colors">FAQ</a>
          <span>•</span>
          <a href="/legal/terms" className="hover:text-foreground transition-colors">Terms</a>
          <span>•</span>
          <a href="/legal/privacy" className="hover:text-foreground transition-colors">Privacy</a>
          <span>•</span>
          <a href="/docs" className="hover:text-foreground transition-colors">Docs</a>
        </div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen gradient-hero flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 text-center">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  )
}
