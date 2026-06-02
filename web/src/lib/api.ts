const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('session_token')
}

async function fetchAPI(path: string, options?: RequestInit) {
  const token = getToken()
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  })
  if (!res.ok) {
    const text = await res.text()
    if (res.status === 401) {
      localStorage.removeItem('session_token')
      window.location.href = '/'
    }
    throw new Error(text)
  }
  return res.json()
}

export interface DebtResponse {
  id: string
  user_id: string
  platform: string
  amount: number
  due_date: string
  installment_current: number | null
  installment_total: number | null
  category: string | null
  notes: string | null
  status: string
  source: string
  created_at: string
  updated_at: string
}

export interface PaymentResponse {
  id: string
  debt_id: string
  amount_paid: number
  paid_at: string
  notes: string | null
}

export interface MonthlySummary {
  total_active: number
  total_amount: number
  paid_this_month: number
  paid_amount: number
  upcoming: DebtResponse[]
}

export async function loginWithToken(token: string) {
  const data = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  }).then(r => { if (!r.ok) throw new Error('Login failed'); return r.json() })
  localStorage.setItem('session_token', data.session_token)
  return data
}

export async function getDebts(status?: string, platform?: string) {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  if (platform) params.set('platform', platform)
  return fetchAPI(`/api/debts?${params}`) as Promise<DebtResponse[]>
}

export async function getSummary() {
  return fetchAPI('/api/debts/summary') as Promise<MonthlySummary>
}

export async function getUpcoming(days = 30) {
  return fetchAPI(`/api/debts/upcoming?days=${days}`) as Promise<DebtResponse[]>
}

export async function getPayments(debtId: string) {
  return fetchAPI(`/api/debts/${debtId}/payments`) as Promise<PaymentResponse[]>
}

export async function updateDebtStatus(id: string, status: string) {
  return fetchAPI(`/api/debts/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }) as Promise<DebtResponse>
}

export async function getUser() {
  return fetchAPI('/api/user/me') as Promise<{
    id: string
    telegram_id: number
    nama: string | null
    phone_number: string | null
  }>
}

export async function updatePhone(phone_number: string) {
  return fetchAPI('/api/user/phone', {
    method: 'PUT',
    body: JSON.stringify({ phone_number }),
  }) as Promise<{ phone_number: string }>
}

export async function getCheckoutUrl() {
  return fetchAPI('/api/polar/checkout') as Promise<{ url: string }>
}
