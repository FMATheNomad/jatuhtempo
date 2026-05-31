'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Plus, Search } from 'lucide-react'

const statusVariant: Record<string, 'active' | 'paid' | 'late'> = {
  active: 'active', paid: 'paid', late: 'late',
}

export default function DebtsPage() {
  const [debts, setDebts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const { getDebts } = await import('@/lib/api')
        const d = await getDebts()
        setDebts(d)
      } catch { /* ignore */ }
      setLoading(false)
    }
    load()
  }, [])

  const filtered = debts.filter(d => {
    if (statusFilter && d.status !== statusFilter) return false
    if (filter && !d.platform.toLowerCase().includes(filter.toLowerCase())) return false
    return true
  })

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold">Utang</h1>
            <MobileNav />
          </div>
        </header>

        <div className="p-4 lg:p-8 animate-fade-in">
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <CardTitle>Daftar Utang</CardTitle>
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <input
                      placeholder="Cari platform..."
                      value={filter}
                      onChange={e => setFilter(e.target.value)}
                      className="h-9 w-40 lg:w-56 rounded-lg border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                  <select
                    value={statusFilter}
                    onChange={e => setStatusFilter(e.target.value)}
                    className="h-9 rounded-lg border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="">Semua</option>
                    <option value="active">Aktif</option>
                    <option value="paid">Lunas</option>
                    <option value="late">Terlambat</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  {[1,2,3,4,5].map(i => <div key={i} className="h-14 bg-secondary rounded-lg animate-pulse" />)}
                </div>
              ) : filtered.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">Tidak ada utang ditemukan</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b text-left text-sm text-muted-foreground">
                        <th className="pb-3 font-medium">Status</th>
                        <th className="pb-3 font-medium">Platform</th>
                        <th className="pb-3 font-medium">Jumlah</th>
                        <th className="pb-3 font-medium">Jatuh Tempo</th>
                        <th className="pb-3 font-medium hidden md:table-cell">Cicilan</th>
                        <th className="pb-3 font-medium hidden md:table-cell">Kategori</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map((d: any) => (
                        <tr key={d.id} className="border-b last:border-0 hover:bg-secondary/30 transition-colors">
                          <td className="py-3">
                            <Badge variant={statusVariant[d.status] || 'default'}>
                              {d.status === 'active' ? 'Aktif' : d.status === 'paid' ? 'Lunas' : 'Terlambat'}
                            </Badge>
                          </td>
                          <td className="py-3 font-medium">{d.platform}</td>
                          <td className="py-3 font-semibold">Rp{d.amount.toLocaleString('id-ID')}</td>
                          <td className="py-3 text-sm text-muted-foreground">{d.due_date}</td>
                          <td className="py-3 text-sm text-muted-foreground hidden md:table-cell">
                            {d.installment_current && d.installment_total
                              ? `${d.installment_current}/${d.installment_total}`
                              : '-'}
                          </td>
                          <td className="py-3 text-sm text-muted-foreground hidden md:table-cell">
                            {d.category || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
