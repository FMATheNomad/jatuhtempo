'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Pencil, X, Check, Shield, ShieldOff } from 'lucide-react'
import { getAllPlatformRates, type PlatformRateResponse, getToken, fetchAPI } from '@/lib/api'

function confidenceLabel(c: number): string {
  if (c >= 0.7) return '🟢 Tinggi'
  if (c >= 0.3) return '🟡 Sedang'
  return '🔴 Rendah'
}

function confidenceColor(c: number): string {
  if (c >= 0.7) return 'text-emerald-600'
  if (c >= 0.3) return 'text-amber-600'
  return 'text-red-600'
}

export default function AdminRatesPage() {
  const [rates, setRates] = useState<PlatformRateResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<string | null>(null)
  const [editForm, setEditForm] = useState({ avg_rate: '', common_type: '' })
  const [saving, setSaving] = useState(false)
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)

  useEffect(() => {
    async function checkAdmin() {
      try {
        const res = await fetch('/api/auth/me', {
          headers: { Authorization: `Bearer ${getToken()}` },
        })
        if (res.ok) {
          const data = await res.json()
          setIsAdmin(data.is_admin === true)
        } else {
          setIsAdmin(false)
        }
      } catch {
        setIsAdmin(false)
      }
    }
    checkAdmin()
  }, [])

  async function load() {
    try {
      const d = await getAllPlatformRates()
      setRates(d)
    } catch { setError('Gagal memuat data suku bunga.') }
    setLoading(false)
  }

  useEffect(() => { if (isAdmin) load() }, [isAdmin])

  async function startEdit(rate: PlatformRateResponse) {
    setEditing(rate.platform)
    setEditForm({ avg_rate: String(rate.avg_rate), common_type: rate.common_type || 'monthly' })
  }

  function cancelEdit() {
    setEditing(null)
    setEditForm({ avg_rate: '', common_type: '' })
  }

  async function saveEdit(platform: string) {
    setSaving(true)
    try {
      await fetchAPI(`/api/admin/platforms/rates/${encodeURIComponent(platform)}`, {
        method: 'PUT',
        body: JSON.stringify({
          avg_rate: parseFloat(editForm.avg_rate) || 0,
          common_type: editForm.common_type || null,
        }),
      })
      setEditing(null)
      load()
    } catch (e: any) { setError(e.message || 'Gagal menyimpan.') }
    setSaving(false)
  }

  if (isAdmin === null) return null

  if (!isAdmin) {
    return (
      <div className="flex">
        <Sidebar />
        <main className="flex-1 min-h-screen">
          <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
            <div className="flex items-center justify-between p-4 lg:px-8">
              <h1 className="text-xl font-semibold flex items-center gap-2">
                <ShieldOff className="w-5 h-5" /> Admin — Suku Bunga
              </h1>
              <MobileNav />
            </div>
          </header>
          <div className="p-4 lg:p-8">
            <Card>
              <CardContent className="text-center py-12">
                <Shield className="w-12 h-12 mx-auto mb-4 text-red-400" />
                <h2 className="text-xl font-semibold mb-2">Akses Ditolak</h2>
                <p className="text-muted-foreground">Halaman ini hanya untuk admin.</p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold flex items-center gap-2">
              <Shield className="w-5 h-5" /> Admin — Suku Bunga Platform
            </h1>
            <MobileNav />
          </div>
        </header>

        <div className="p-4 lg:p-8 animate-fade-in">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-sm text-red-700">{error}</div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Data Suku Bunga yang Dipelajari</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">{[1,2,3,4,5].map(i => <div key={i} className="h-14 bg-secondary rounded-lg animate-pulse" />)}</div>
              ) : rates.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <p>Belum ada data suku bunga.</p>
                  <p className="text-xs mt-1">Data akan terkumpul saat user menambahkan utang dengan bunga.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b text-left text-sm text-muted-foreground">
                        <th className="pb-3 font-medium">Platform</th>
                        <th className="pb-3 font-medium">Rata-rata Bunga</th>
                        <th className="pb-3 font-medium">Tipe Umum</th>
                        <th className="pb-3 font-medium">Sampel</th>
                        <th className="pb-3 font-medium">Confidence</th>
                        <th className="pb-3 font-medium">Aksi</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rates.map(r => (
                        <tr key={r.platform} className="border-b last:border-0 hover:bg-secondary/30 transition-colors">
                          <td className="py-3 font-medium">{r.platform}</td>
                          {editing === r.platform ? (
                            <>
                              <td className="py-3">
                                <input
                                  value={editForm.avg_rate}
                                  onChange={e => setEditForm({ ...editForm, avg_rate: e.target.value })}
                                  type="number" step="0.01"
                                  className="h-8 w-20 rounded border border-input bg-background px-2 text-sm"
                                />
                              </td>
                              <td className="py-3">
                                <select
                                  value={editForm.common_type}
                                  onChange={e => setEditForm({ ...editForm, common_type: e.target.value })}
                                  className="h-8 rounded border border-input bg-background px-2 text-sm"
                                >
                                  <option value="daily">Harian</option>
                                  <option value="monthly">Bulanan</option>
                                  <option value="yearly">Tahunan</option>
                                  <option value="flat">Flat</option>
                                </select>
                              </td>
                            </>
                          ) : (
                            <>
                              <td className="py-3 font-semibold">{r.avg_rate}%</td>
                              <td className="py-3 text-sm text-muted-foreground">
                                {r.common_type ? {daily:'Harian',monthly:'Bulanan',yearly:'Tahunan',flat:'Flat'}[r.common_type as string] || r.common_type : '-'}
                              </td>
                            </>
                          )}
                          <td className="py-3 text-sm">{r.sample_count}</td>
                          <td className="py-3 text-sm">
                            <span className={confidenceColor(r.confidence)}>
                              {confidenceLabel(r.confidence)} ({(r.confidence * 100).toFixed(0)}%)
                            </span>
                          </td>
                          <td className="py-3">
                            {editing === r.platform ? (
                              <div className="flex items-center gap-1">
                                <button onClick={() => saveEdit(r.platform)} disabled={saving} className="min-h-[36px] min-w-[36px] flex items-center justify-center rounded-lg hover:bg-emerald-100 text-emerald-600" title="Simpan">
                                  <Check className="w-4 h-4" />
                                </button>
                                <button onClick={cancelEdit} className="min-h-[36px] min-w-[36px] flex items-center justify-center rounded-lg hover:bg-red-100 text-red-600" title="Batal">
                                  <X className="w-4 h-4" />
                                </button>
                              </div>
                            ) : (
                              <button onClick={() => startEdit(r)} className="min-h-[36px] min-w-[36px] flex items-center justify-center rounded-lg hover:bg-blue-100 text-blue-600" title="Edit">
                                <Pencil className="w-4 h-4" />
                              </button>
                            )}
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
