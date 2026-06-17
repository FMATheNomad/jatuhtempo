'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Bell, Calendar, AlertTriangle, CheckCircle2 } from 'lucide-react'
import type { DebtResponse } from '@/lib/api'

const statusVariant: Record<string, 'active' | 'paid' | 'late'> = {
  active: 'active', paid: 'paid', late: 'late',
}

export default function UpcomingPage() {
  const [debts, setDebts] = useState<DebtResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const { getUpcoming } = await import('@/lib/api')
        const d = await getUpcoming(30)
        let filtered = d
        if (statusFilter) filtered = d.filter((x: any) => x.status === statusFilter)
        setDebts(filtered)
      } catch { setError('Gagal memuat data.') }
      setLoading(false)
    }
    load()
  }, [statusFilter])

  const totalAmount = debts.reduce((s, d) => s + d.amount, 0)

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold flex items-center gap-2">
              <Bell className="w-5 h-5" /> Akan Datang
            </h1>
            <div className="flex items-center gap-3">
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className="min-h-[44px] rounded-lg border border-input bg-background px-3 text-sm"
              >
                <option value="">Semua</option>
                <option value="active">Aktif</option>
                <option value="late">Terlambat</option>
                <option value="paid">Lunas</option>
              </select>
              <MobileNav />
            </div>
          </div>
        </header>

        <div className="p-4 lg:p-8 space-y-6 animate-fade-in">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">{error}</div>
          )}

          {/* Summary Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-muted-foreground">Tagihan Mendatang</p>
                  <Bell className="w-4 h-4 text-muted-foreground" />
                </div>
                <p className="text-2xl font-bold">{debts.length}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-muted-foreground">Total Jumlah</p>
                  <Calendar className="w-4 h-4 text-muted-foreground" />
                </div>
                <p className="text-2xl font-bold">Rp{totalAmount.toLocaleString('id-ID')}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-muted-foreground">Rata-rata per Tagihan</p>
                  <AlertTriangle className="w-4 h-4 text-muted-foreground" />
                </div>
                <p className="text-2xl font-bold">
                  Rp{(debts.length > 0 ? Math.round(totalAmount / debts.length) : 0).toLocaleString('id-ID')}
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Jatuh Tempo dalam 30 Hari
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">{[1,2,3,4,5].map(i => <div key={i} className="h-14 bg-secondary rounded-lg animate-pulse" />)}</div>
              ) : debts.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <CheckCircle2 className="w-12 h-12 mx-auto mb-4 opacity-30" />
                  <p>Tidak ada tagihan dalam 30 hari ke depan.</p>
                </div>
              ) : (
                <>
                  {/* Mobile: Card list */}
                  <div className="space-y-3 lg:hidden">
                    {[...debts].sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime()).map(d => (
                      <div key={d.id} className="border rounded-xl p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={statusVariant[d.status] || 'default'}>
                              {d.status === 'active' ? 'Aktif' : d.status === 'paid' ? 'Lunas' : 'Terlambat'}
                            </Badge>
                            <span className="font-semibold">{d.platform}</span>
                          </div>
                          <span className="font-bold">Rp{d.amount.toLocaleString('id-ID')}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {d.due_date}
                          </span>
                          <div className="flex items-center gap-2">
                            {d.installment_current && d.installment_total && (
                              <span>{d.installment_current}/{d.installment_total}</span>
                            )}
                            {d.interest_rate && (
                              <span className="text-accent font-medium">{d.interest_rate}%{d.interest_type ? '/' + {daily:'hari',monthly:'bln',yearly:'thn',flat:'flat'}[d.interest_type as string] : ''}</span>
                            )}
                          </div>
                        </div>
                        {d.category && <p className="text-xs text-muted-foreground">{d.category}</p>}
                      </div>
                    ))}
                  </div>
                  {/* Desktop: Table */}
                  <div className="hidden lg:block overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b text-left text-sm text-muted-foreground">
                          <th className="pb-3 font-medium">Status</th>
                          <th className="pb-3 font-medium">Platform</th>
                          <th className="pb-3 font-medium">Jumlah</th>
                          <th className="pb-3 font-medium">Jatuh Tempo</th>
                          <th className="pb-3 font-medium">Cicilan</th>
                          <th className="pb-3 font-medium">Bunga <span className="text-xs opacity-60">(confidence)</span></th>
                          <th className="pb-3 font-medium">Kategori</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[...debts]
                          .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
                          .map(d => (
                            <tr key={d.id} className="border-b last:border-0 hover:bg-secondary/30 transition-colors">
                              <td className="py-3">
                                <Badge variant={statusVariant[d.status] || 'default'}>
                                  {d.status === 'active' ? 'Aktif' : d.status === 'paid' ? 'Lunas' : 'Terlambat'}
                                </Badge>
                              </td>
                              <td className="py-3 font-medium">{d.platform}</td>
                              <td className="py-3 font-semibold">Rp{d.amount.toLocaleString('id-ID')}</td>
                              <td className="py-3 text-sm text-muted-foreground">{d.due_date}</td>
                              <td className="py-3 text-sm text-muted-foreground">
                                {d.installment_current && d.installment_total ? `${d.installment_current}/${d.installment_total}` : '-'}
                              </td>
                              <td className="py-3 text-sm text-muted-foreground">
                                {d.interest_rate ? <span className="text-accent font-medium">{d.interest_rate}%{d.interest_type ? '/' + {daily:'hari',monthly:'bln',yearly:'thn',flat:'flat'}[d.interest_type as string] : ''} <span className="text-xs opacity-50">{d.interest_rate < 1 ? '🟢' : d.interest_rate < 3 ? '🟡' : '🔴'}</span></span> : '-'}
                              </td>
                              <td className="py-3 text-sm text-muted-foreground">{d.category || '-'}</td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
