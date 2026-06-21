'use client'

import { useEffect, useState, useMemo } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingDown, Sparkles, Calculator, Calendar, AlertTriangle } from 'lucide-react'
import { fetchAPI, getToken } from '@/lib/api'

function calcMonthly(debt: any): number {
  if (debt.installment_total && debt.installment_total > 0) {
    return Math.round(debt.amount / debt.installment_total)
  }
  if (debt.status === 'paid') return 0
  return debt.amount
}

function calcRemaining(debt: any): number {
  if (debt.installment_total && debt.installment_current) {
    return debt.installment_total - debt.installment_current + (debt.status === 'active' ? 0 : 0)
  }
  return 1
}

export default function StrategyPage() {
  const [debts, setDebts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [extra, setExtra] = useState(0)
  const [income, setIncome] = useState(0)
  const [expense, setExpense] = useState(0)
  const [strategy, setStrategy] = useState<'snowball' | 'avalanche'>('snowball')

  useEffect(() => {
    fetchAPI('/api/debts').then(d => { setDebts(d.data || d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const active = debts.filter(d => d.status === 'active')
  const totalDebt = active.reduce((s, d) => s + d.amount, 0)
  const totalMonthly = active.reduce((s, d) => s + calcMonthly(d), 0)

  const sorted = useMemo(() => {
    if (strategy === 'avalanche') {
      return [...active].sort((a, b) => (b.interest_rate || 0) - (a.interest_rate || 0))
    }
    return [...active].sort((a, b) => a.amount - b.amount)
  }, [active, strategy])

  const simulation = useMemo(() => {
    if (extra <= 0) return null
    let remaining = sorted.map(d => ({ ...d, left: d.amount }))
    let monthly = extra
    let months = 0
    let totalPaid = 0

    while (remaining.length > 0 && months < 600) {
      months++
      let budget = monthly
      for (const d of remaining) {
        const min = Math.min(calcMonthly(d), d.left)
        if (budget >= min) {
          d.left -= min
          budget -= min
          totalPaid += min
        }
      }
      if (budget > 0 && remaining.length > 0) {
        remaining[0].left -= budget
        totalPaid += budget
      }
      remaining = remaining.filter(d => d.left > 0)
    }

    if (months >= 600) return { tooLong: true }
    const payoffDate = new Date()
    payoffDate.setMonth(payoffDate.getMonth() + months)

    return { months, payoffDate, totalPaid, interestSaved: Math.max(0, totalPaid - totalDebt) }
  }, [sorted, extra, totalDebt])

  const incomeSim = useMemo(() => {
    if (income <= 0 || expense <= 0) return null
    const disposable = income - expense
    if (disposable <= 0) return { error: 'Pengeluaran lebih besar dari pendapatan' }
    let remaining = sorted.map(d => ({ ...d, left: d.amount }))
    let months = 0

    while (remaining.length > 0 && months < 600) {
      months++
      let budget = disposable
      for (const d of remaining) {
        const min = Math.min(calcMonthly(d), d.left)
        if (budget >= min) { d.left -= min; budget -= min }
      }
      if (budget > 0 && remaining.length > 0) remaining[0].left -= budget
      remaining = remaining.filter(d => d.left > 0)
    }
    if (months >= 600) return { tooLong: true }
    const date = new Date(); date.setMonth(date.getMonth() + months)
    return { months, date, percent: Math.round((1 - months / 600) * 100) }
  }, [sorted, income, expense])

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold">Strategi Lunasi</h1>
            <MobileNav />
          </div>
        </header>

        <div className="p-4 lg:p-8 space-y-6 animate-fade-in">
          {loading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-secondary rounded-lg animate-pulse" />)}</div>
          ) : active.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12 text-muted-foreground">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>Belum ada utang aktif. Tambah utang dulu untuk lihat strategi.</p>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Summary */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <p className="text-sm text-muted-foreground">Total Utang</p>
                    <p className="text-2xl font-bold">Rp{totalDebt.toLocaleString('id-ID')}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <p className="text-sm text-muted-foreground">Total Per Bulan</p>
                    <p className="text-2xl font-bold">Rp{totalMonthly.toLocaleString('id-ID')}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <p className="text-sm text-muted-foreground">Jumlah Utang</p>
                    <p className="text-2xl font-bold">{active.length} tagihan</p>
                  </CardContent>
                </Card>
              </div>

              {/* Payoff Order (Snowball/Avalanche) */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingDown className="w-5 h-5" />
                    Urutan Pelunasan — {strategy === 'snowball' ? 'Snowball' : 'Avalanche'}
                  </CardTitle>
                  <div className="flex items-center gap-2 mt-2">
                    <button
                      onClick={() => setStrategy('snowball')}
                      className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                        strategy === 'snowball'
                          ? 'bg-primary text-primary-foreground shadow-sm'
                          : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
                      }`}
                    >
                      Snowball
                    </button>
                    <button
                      onClick={() => setStrategy('avalanche')}
                      className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                        strategy === 'avalanche'
                          ? 'bg-primary text-primary-foreground shadow-sm'
                          : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
                      }`}
                    >
                      Avalanche
                    </button>
                    <span className="text-xs text-muted-foreground ml-1">
                      {strategy === 'snowball' ? 'Urut dari jumlah terkecil' : 'Urut dari bunga tertinggi'}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {sorted.map((d, i) => (
                      <div key={d.id} className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                        <div className="flex items-center gap-3">
                          <span className="w-7 h-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">{i + 1}</span>
                          <div>
                            <p className="font-medium text-sm">{d.platform}</p>
                            <p className="text-xs text-muted-foreground">{d.category || '-'}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">Rp{d.amount.toLocaleString('id-ID')}</p>
                          <p className="text-xs text-muted-foreground">
                            {d.installment_current && d.installment_total
                              ? `${d.installment_current}/${d.installment_total}`
                              : '-'}
                            {d.interest_rate && (
                              <span className="text-accent ml-1">
                                {d.interest_rate}%{d.interest_type ? '/' + {daily:'hari',monthly:'bln',yearly:'thn',flat:'flat'}[d.interest_type as string] : ''}
                              </span>
                            )}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Simulator */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calculator className="w-5 h-5" />
                    Simulator Bebas Utang
                  </CardTitle>
                  <CardDescription>Atur tambahan bayaran per bulan untuk lihat proyeksi</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Tambahan Bayaran per Bulan</label>
                    <input
                      type="range"
                      min={0}
                      max={Math.max(totalMonthly * 3, 500000)}
                      step={50000}
                      value={extra}
                      onChange={e => setExtra(Number(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>Rp0</span>
                      <span className="font-semibold text-foreground">Rp{extra.toLocaleString('id-ID')}</span>
                      <span>Rp{(totalMonthly * 3).toLocaleString('id-ID')}</span>
                    </div>
                  </div>

                  {simulation && 'tooLong' in simulation && (
                    <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                      <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle className="w-5 h-5 text-amber-600" />
                        <h3 className="font-semibold text-amber-800">Proyeksi Tidak Tersedia</h3>
                      </div>
                      <p className="text-sm text-amber-700">
                        Proyeksi tidak tersedia untuk jangka waktu lebih dari 600 bulan (50 tahun).
                        Coba tingkatkan jumlah tambahan bayaran per bulan.
                      </p>
                    </div>
                  )}
                  {simulation && !('tooLong' in simulation) && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
                      <div className="flex items-center gap-2 mb-3">
                        <Calendar className="w-5 h-5 text-emerald-600" />
                        <h3 className="font-semibold text-emerald-800">Proyeksi Bebas Utang</h3>
                      </div>
                      <p className="text-3xl font-bold text-emerald-700 mb-1">
                        {(simulation as any).payoffDate.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' })}
                      </p>
                      <p className="text-sm text-emerald-600">
                        {(simulation as any).months} bulan lagi • Total dibayar Rp{(simulation as any).totalPaid.toLocaleString('id-ID')}
                      </p>
                    </div>
                  )}

                  {extra === 0 && (
                    <p className="text-sm text-muted-foreground text-center">
                      Geser slider untuk lihat proyeksi tanggal bebas utang
                    </p>
                  )}

                  {/* Income-based simulator */}
                  <div className="border-t pt-6">
                    <h3 className="text-sm font-medium mb-3">Simulasi Berdasarkan Pendapatan</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                      <div>
                        <label className="text-xs text-muted-foreground mb-1 block">Pendapatan / Bulan</label>
                        <input
                          value={income || ''}
                          onChange={e => setIncome(Number(e.target.value))}
                          placeholder="Rp"
                          type="number"
                          className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-muted-foreground mb-1 block">Pengeluaran / Bulan</label>
                        <input
                          value={expense || ''}
                          onChange={e => setExpense(Number(e.target.value))}
                          placeholder="Rp"
                          type="number"
                          className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm"
                        />
                      </div>
                    </div>

                    {incomeSim && 'error' in incomeSim && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">{incomeSim.error}</div>
                    )}
                    {incomeSim && 'tooLong' in incomeSim && (
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-700">
                        Proyeksi tidak tersedia untuk jangka waktu lebih dari 600 bulan (50 tahun).
                        Coba tingkatkan pendapatan atau kurangi pengeluaran.
                      </div>
                    )}
                    {incomeSim && !('error' in incomeSim) && !('tooLong' in incomeSim) && (
                      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                        <p className="text-sm font-medium text-blue-800">Dengan pendapatan saat ini, kamu bisa bebas utang:</p>
                        <p className="text-2xl font-bold text-blue-700">{(incomeSim as any).date.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' })}</p>
                        <p className="text-sm text-blue-600">{(incomeSim as any).months} bulan lagi</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
