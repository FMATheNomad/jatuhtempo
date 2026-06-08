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
      .catch(() => setStatus('Token tidak valid atau kadaluarsa. Ulangi /login di Telegram.'))
  }, [token, router])

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
        <h1 className="text-xl font-bold mb-2">Login ke Dashboard</h1>
        <p className="text-muted-foreground mb-6">
          Dashboard hanya bisa diakses melalui link dari bot Telegram.
        </p>
        <div className="bg-secondary rounded-xl p-4 mb-6 text-left space-y-3 text-sm">
          <div className="flex gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold shrink-0">1</span>
            <span>Buka Telegram dan cari <strong>{BOT_USERNAME}</strong></span>
          </div>
          <div className="flex gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold shrink-0">2</span>
            <span>Ketik perintah <code className="bg-muted px-1 rounded">/login</code></span>
          </div>
          <div className="flex gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold shrink-0">3</span>
            <span>Klik link yang dikirim bot untuk masuk ke dashboard</span>
          </div>
        </div>
        <a
          href={`https://t.me/${BOT_USERNAME.replace('@', '')}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center w-full h-10 rounded-lg bg-accent text-accent-foreground font-medium text-sm hover:opacity-90 transition-opacity"
        >
          Buka Telegram Sekarang
        </a>
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
