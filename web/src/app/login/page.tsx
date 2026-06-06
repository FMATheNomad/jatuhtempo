'use client'

import { Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

function LoginContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState('Memproses...')

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) {
      setStatus('Token tidak ditemukan. Gunakan /login di Telegram untuk mendapatkan link.')
      return
    }

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    fetch(`${API_BASE}/api/auth/login`, {
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
  }, [searchParams, router])

  return (
    <div className="min-h-screen gradient-hero flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 text-center animate-fade-in">
        <img src="/assets/logo.png" alt="JatuhTempo" className="h-12 mx-auto mb-6" />
        <p className="text-muted-foreground">{status}</p>
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
