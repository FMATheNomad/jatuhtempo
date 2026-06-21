'use client'

import { Suspense, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useEffect } from 'react'

const BOT_USERNAME = '@JatuhTempo_bot'

function LoginContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get('token')
  const modeParam = searchParams.get('mode')
  const [status, setStatus] = useState(token ? 'Memproses...' : '')
  const [mode, setMode] = useState<'login' | 'register'>(modeParam === 'register' ? 'register' : 'login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nama, setNama] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState(false)

  async function handleDemoLogin() {
    setDemoLoading(true)
    try {
      const res = await fetch('/api/auth/login-web', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'demo@jatuhtempo.app', password: 'demo123' }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Gagal login demo')
      localStorage.setItem('session_token', data.session_token)
      router.push('/')
    } catch (e: any) { setError(e.message) }
    setDemoLoading(false)
  }

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
      <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4 animate-fade-in text-slate-900">
        <img src="/assets/logo.webp" alt="JatuhTempo" className="h-12 mx-auto mb-6" />

        <h1 className="text-xl font-bold mb-1">{mode === 'login' ? 'Masuk' : 'Daftar'}</h1>
        <p className="text-sm text-slate-500 mb-6">
          {mode === 'login' ? 'Sudah punya akun? Masuk dengan email.' : 'Buat akun baru untuk mulai.'}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">Nama</label>
              <input value={nama} onChange={e => setNama(e.target.value)} className="w-full h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500" />
            </div>
          )}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1 block">Email</label>
            <input value={email} onChange={e => setEmail(e.target.value)} type="email" required className="w-full h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500" />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1 block">Password</label>
            <input value={password} onChange={e => setPassword(e.target.value)} type="password" required minLength={6} className="w-full h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500" />
            {mode === 'login' && (
              <p className="text-xs text-slate-500 mt-1.5">
                Lupa password?{' '}
                <a href="/reset-password" className="text-teal-600 hover:underline">
                  Reset di sini
                </a>
              </p>
            )}
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button type="submit" disabled={loading} className="w-full min-h-[44px] rounded-lg bg-teal-600 text-white font-medium text-sm hover:bg-teal-700 disabled:opacity-50 transition-colors">
            {loading ? 'Memproses...' : mode === 'login' ? 'Masuk' : 'Daftar'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }} className="text-sm text-teal-600 hover:underline">
            {mode === 'login' ? 'Belum punya akun? Daftar' : 'Sudah punya akun? Masuk'}
          </button>
        </div>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200" /></div>
          <div className="relative flex justify-center text-xs text-slate-500"><span className="bg-white px-2">atau</span></div>
        </div>

        <a href={`https://t.me/${BOT_USERNAME.replace('@', '')}`} target="_blank" className="flex items-center justify-center gap-2 w-full min-h-[44px] rounded-lg border border-slate-300 bg-white text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">
          Login dengan Telegram
        </a>

        <div className="mt-3">
          <button
            onClick={handleDemoLogin}
            disabled={demoLoading}
            className="flex items-center justify-center gap-2 w-full h-10 rounded-lg border-2 border-dashed border-teal-400 bg-teal-50 text-sm font-medium text-teal-700 hover:bg-teal-100 transition-all disabled:opacity-50"
          >
            {demoLoading ? 'Memproses...' : '🔑 Login Demo (User Biasa)'}
          </button>
        </div>

        <p className="text-xs text-slate-500 text-center mt-4">
          Setelah login, tautkan Telegram di menu Pengaturan.
        </p>

        <div className="mt-6 pt-4 border-t border-slate-200 text-xs text-slate-500 flex items-center justify-center gap-2">
          <a href="/faq" className="hover:text-slate-700 transition-colors">FAQ</a>
          <span>•</span>
          <a href="/legal/terms" className="hover:text-slate-700 transition-colors">Terms</a>
          <span>•</span>
          <a href="/legal/privacy" className="hover:text-slate-700 transition-colors">Privacy</a>
          <span>•</span>
          <a href="/docs" className="hover:text-slate-700 transition-colors">Docs</a>
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
