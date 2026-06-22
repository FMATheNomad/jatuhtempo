'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, CreditCard, TrendingUp, CheckCircle2 } from 'lucide-react'

export default function MonthlyPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const { getSummary } = await import('@/lib/api')
        const d = await getSummary()
        setData(d)
      } catch { setError('Gagal memuat data bulanan.') }
      setLoading(false)
    }
    load()
  }, [])

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold flex items-center gap-2">
              <Calendar className="w-5 h-5" /> Ringkasan Bulanan
            </h1>
            <MobileNav />
          </div>
        </header>

        <div className="p-4 lg:p-8 space-y-6 animate-fade-in">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">{error}</div>
          )}

          {loading ? (
            <div className="space-y-3">{[1,2,3,4].map(i => <div key={i} className="h-20 bg-secondary rounded-lg animate-pulse" />)}</div>
          ) : !data ? (
            <Card>
              <CardContent className="text-center py-12 text-muted-foreground">
                <Calendar className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>Belum ada data bulanan.</p>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm text-muted-foreground">Utang Aktif</p>
                      <CreditCard className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <p className="text-2xl font-bold">{data.total_active}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm text-muted-foreground">Total Jumlah</p>
                      <TrendingUp className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <p className="text-2xl font-bold">Rp{(data.total_amount || 0).toLocaleString('id-ID')}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm text-muted-foreground">Dibayar Bulan Ini</p>
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    </div>
                    <p className="text-2xl font-bold text-emerald-600">{data.paid_this_month} kali</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm text-muted-foreground">Total Dibayar</p>
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    </div>
                    <p className="text-2xl font-bold text-emerald-600">Rp{(data.paid_amount || 0).toLocaleString('id-ID')}</p>
                  </CardContent>
                </Card>
              </div>

              {/* Upcoming this month */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Tagihan Bulan Ini
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {data.upcoming && data.upcoming.length > 0 ? (
                    <div className="space-y-3">
                      {/* Mobile: Card list */}
                      <div className="space-y-2 lg:hidden">
                        {data.upcoming.map((d: any) => (
                          <div key={d.id} className="border rounded-xl p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-semibold">{d.platform}</span>
                              <span className="font-bold">Rp{d.amount.toLocaleString('id-ID')}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm text-muted-foreground">
                              <span>Jatuh tempo {d.due_date}</span>
                              <Badge variant={d.status === 'late' ? 'late' : d.status === 'paid' ? 'paid' : 'active'}>
                                {d.status === 'late' ? 'Terlambat' : d.status === 'paid' ? 'Lunas' : 'Aktif'}
                              </Badge>
                            </div>
                            {d.installment_current && d.installment_total && (
                              <p className="text-xs text-muted-foreground mt-1">
                                Cicilan {d.installment_current}/{d.installment_total}
                              </p>
                            )}
                            {d.interest_rate && (
                              <p className="text-xs text-accent font-medium mt-1">
                                Bunga {d.interest_rate}%{d.interest_type ? '/' + {daily:'hari',monthly:'bln',yearly:'thn',flat:'flat'}[d.interest_type as string] || d.interest_type : ''}
                              </p>
                            )}
                            {d.interest_rate && d.status !== 'paid' && (
                              <p className="text-xs text-muted-foreground mt-0.5">
                                {d.interest_rate}%/{d.interest_type === 'monthly' ? 'bln' : d.interest_type === 'daily' ? 'hari' : d.interest_type === 'yearly' ? 'thn' : 'flat'}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                      {/* Desktop: Table */}
                      <div className="hidden lg:block overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b text-left text-sm text-muted-foreground">
                              <th className="pb-3 font-medium">Platform</th>
                              <th className="pb-3 font-medium">Jumlah</th>
                              <th className="pb-3 font-medium">Jatuh Tempo</th>
                              <th className="pb-3 font-medium">Cicilan</th>
                              <th className="pb-3 font-medium">Bunga <span className="text-xs opacity-60">(confidence)</span></th>
                              <th className="pb-3 font-medium">Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.upcoming.map((d: any) => (
                              <tr key={d.id} className="border-b last:border-0 hover:bg-secondary/30 transition-colors">
                                <td className="py-3 font-medium">{d.platform}</td>
                                <td className="py-3 font-semibold">Rp{d.amount.toLocaleString('id-ID')}</td>
                                <td className="py-3 text-sm text-muted-foreground">{d.due_date}</td>
                                <td className="py-3 text-sm text-muted-foreground">
                                  {d.installment_current && d.installment_total ? `${d.installment_current}/${d.installment_total}` : '-'}
                                </td>
                                <td className="py-3 text-sm text-muted-foreground">
                                  {d.interest_rate ? <span className="text-accent font-medium">{d.interest_rate}%{d.interest_type ? '/' + {daily:'hari',monthly:'bln',yearly:'thn',flat:'flat'}[d.interest_type as string] : ''}</span> : '-'}
                                </td>
                                <td className="py-3">
                                  <Badge variant={d.status === 'late' ? 'late' : d.status === 'paid' ? 'paid' : 'active'}>
                                    {d.status === 'late' ? 'Terlambat' : d.status === 'paid' ? 'Lunas' : 'Aktif'}
                                  </Badge>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                      Tidak ada tagihan bulan ini.
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
