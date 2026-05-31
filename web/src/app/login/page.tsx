'use client'

import { Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { loginWithToken } from '@/lib/api'

function LoginContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState('Memproses...')

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) {
      setStatus('Token tidak ditemukan.')
      return
    }
    loginWithToken(token)
      .then(() => {
        setStatus('Berhasil! Mengarahkan...')
        setTimeout(() => router.push('/'), 1000)
      })
      .catch(() => setStatus('Token tidak valid atau kadaluarsa.'))
  }, [searchParams, router])

  return (
    <div className="min-h-screen gradient-hero flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 text-center animate-fade-in">
        <div className="w-16 h-16 rounded-2xl gradient-card flex items-center justify-center mx-auto mb-6">
          <span className="text-white font-bold text-2xl">JT</span>
        </div>
        <p className="text-muted-foreground">{status}</p>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen gradient-hero flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 text-center animate-fade-in">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  )
}
