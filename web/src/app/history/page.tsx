'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function HistoryPage() {
  const [debts, setDebts] = useState<any[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [payments, setPayments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const { getDebts } = await import('@/lib/api')
        const d = await getDebts()
        setDebts(d.filter((x: any) => x.status === 'paid'))
      } catch { /* ignore */ }
      setLoading(false)
    }
    load()
  }, [])

  async function showPayments(debtId: string) {
    setSelected(debtId)
    try {
      const { getPayments } = await import('@/lib/api')
      const p = await getPayments(debtId)
      setPayments(p)
    } catch { /* ignore */ }
  }

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold">Riwayat Pembayaran</h1>
            <MobileNav />
          </div>
        </header>

        <div className="p-4 lg:p-8 animate-fade-in">
          <Card>
            <CardHeader>
              <CardTitle>Utang Lunas</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  {[1,2,3].map(i => <div key={i} className="h-12 bg-secondary rounded-lg animate-pulse" />)}
                </div>
              ) : debts.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">Belum ada utang lunas</div>
              ) : (
                <div className="space-y-2">
                  {debts.map((d: any) => (
                    <div key={d.id}>
                      <button
                        onClick={() => showPayments(d.id)}
                        className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-secondary/50 transition-colors text-left"
                      >
                        <div>
                          <p className="font-medium">{d.platform}</p>
                          <p className="text-xs text-muted-foreground">Jatuh tempo {d.due_date}</p>
                        </div>
                        <p className="font-semibold">Rp{d.amount.toLocaleString('id-ID')}</p>
                      </button>
                      {selected === d.id && payments.length > 0 && (
                        <div className="ml-4 pl-4 border-l space-y-1 mb-2">
                          {payments.map((p: any) => (
                            <div key={p.id} className="text-sm text-muted-foreground py-1">
                              ✓ Rp{p.amount_paid.toLocaleString('id-ID')} — {new Date(p.paid_at).toLocaleDateString('id-ID')}
                              {p.notes && <span> — {p.notes}</span>}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
