'use client'

import { Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

const BOT_USERNAME = '@JatuhTempo_bot'

function LoginContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get('token')
  const [status, setStatus] = useState(token ? 'Memproses...' : '')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!token) return
    fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })
      .then(res => {
        if (!res.ok) throw new Error('Invalid token')
        return res.json()
      })
      .then(data => {
        localStorage.setItem('session_token', data.session_token)
        setStatus('Berhasil! Mengarahkan...')
        setTimeout(() => router.push('/'), 1000)
      })
      .catch(() => setStatus('Token tidak valid atau kadaluarsa.'))
  }, [token, router])

  async function handleGuest() {
    setLoading(true)
    try {
      const res = await fetch('/api/auth/guest', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
      const data = await res.json()
      localStorage.setItem('session_token', data.session_token)
      router.push('/')
    } catch {
      setStatus('Gagal membuat akun guest.')
    }
    setLoading(false)
  }

  if (token) {
    return (
      <div className="min-h-screen gradient-hero flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 text-center animate-fade-in">
          <img src="/assets/logo.png" alt="JatuhTempo" className="h-12 mx-auto mb-6" />
          <p className="text-muted-foreground">{status}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen gradient-hero flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4 text-center animate-fade-in">
        <img src="/assets/logo.png" alt="JatuhTempo" className="h-12 mx-auto mb-6" />
        <h1 className="text-xl font-bold mb-2">Mulai Kelola Utang</h1>
        <p className="text-muted-foreground mb-6 text-sm">
          Pilih cara masuk untuk melanjutkan
        </p>

        <div className="space-y-3">
          <a
            href={`https://t.me/${BOT_USERNAME.replace('@', '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-3 w-full h-12 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 transition-opacity"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
            Login dengan Telegram
          </a>

          <button
            onClick={handleGuest}
            disabled={loading}
            className="w-full h-12 rounded-lg border border-border bg-background font-medium text-sm hover:bg-secondary transition-colors disabled:opacity-50"
          >
            {loading ? 'Memproses...' : 'Lanjut sebagai Tamu'}
          </button>
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          Guest: data tersimpan di perangkat ini saja.
          <br />Bisa ditautkan dengan Telegram nanti di Pengaturan.
        </p>
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
