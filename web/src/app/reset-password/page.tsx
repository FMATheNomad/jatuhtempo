'use client'

import { Suspense, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'

function ResetContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get('token')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password.length < 6) { setMessage('Password minimal 6 karakter'); return }
    if (password !== confirm) { setMessage('Password tidak cocok'); return }
    setStatus('loading'); setMessage('')
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Gagal')
      setStatus('success')
      setMessage('Password berhasil direset!')
      setTimeout(() => router.push('/login'), 2000)
    } catch (e: any) { setStatus('error'); setMessage(e.message) }
  }

  if (!token) return (
    <div className="min-h-screen gradient-hero flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 text-center text-slate-900">
        <p className="text-slate-500">Link reset tidak valid. Coba minta reset password lagi.</p>
        <a href="/login" className="mt-4 inline-block text-teal-600 hover:underline">Kembali ke Login</a>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen gradient-hero flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4 animate-fade-in text-slate-900">
        <h1 className="text-xl font-bold mb-1">Reset Password</h1>
        <p className="text-sm text-slate-500 mb-6">Masukkan password baru kamu.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1 block">Password Baru</label>
            <input value={password} onChange={e => setPassword(e.target.value)} type="password" required minLength={6} className="w-full h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500" />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1 block">Konfirmasi Password</label>
            <input value={confirm} onChange={e => setConfirm(e.target.value)} type="password" required minLength={6} className="w-full h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500" />
          </div>

          {message && (
            <p className={`text-sm ${status === 'success' ? 'text-emerald-600' : 'text-red-600'}`}>{message}</p>
          )}

          <button type="submit" disabled={status === 'loading'} className="w-full min-h-[44px] rounded-lg bg-teal-600 text-white font-medium text-sm hover:bg-teal-700 disabled:opacity-50 transition-colors">
            {status === 'loading' ? 'Meriset...' : 'Reset Password'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen gradient-hero flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-sm mx-4 text-center"><p className="text-slate-500">Loading...</p></div>
      </div>
    }>
      <ResetContent />
    </Suspense>
  )
}
