'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Plus, Search, Pencil, Trash2, Check, AlertTriangle, X, Upload } from 'lucide-react'
import type { DebtResponse } from '@/lib/api'

const statusVariant: Record<string, 'active' | 'paid' | 'late'> = {
  active: 'active', paid: 'paid', late: 'late',
}

const API = process.env.NEXT_PUBLIC_API_URL || ''

function token() {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem('session_token') || ''
}

async function api(path: string, options?: RequestInit) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
      ...options?.headers,
    },
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export default function DebtsPage() {
  const [debts, setDebts] = useState<DebtResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [form, setForm] = useState({ platform: '', amount: '', due_date: '', category: '', notes: '' })
  const [ocrPreview, setOcrPreview] = useState<any>(null)
  const [ocrLoading, setOcrLoading] = useState(false)
  const [celebration, setCelebration] = useState<{ platform: string; count: number } | null>(null)

  const activeDebts = debts.filter(d => d.status !== 'paid')
  const paidDebts = debts.filter(d => d.status === 'paid')

  async function load() {
    try {
      const params = new URLSearchParams()
      if (statusFilter) params.set('status', statusFilter)
      if (filter) params.set('platform', filter)
      const d = await api(`/api/debts?${params}`)
      setDebts(d)
    } catch { setError('Gagal memuat data.') }
    setLoading(false)
  }

  useEffect(() => { load() }, [statusFilter, filter])

  async function handleStatus(id: string, status: string, platform: string) {
    try {
      await api(`/api/debts/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) })
      if (status === 'paid') {
        const paid = debts.filter(d => d.status === 'paid').length + 1
        setCelebration({ platform, count: paid })
      }
      load()
    } catch { setError('Gagal update status.') }
  }

  async function handleDelete(id: string) {
    if (!confirm('Hapus utang ini?')) return
    try {
      setLoading(true)
      await api(`/api/debts/${id}`, { method: 'DELETE' })
      load()
    } catch { setError('Gagal hapus.') }
  }

  async function handleSave() {
    const data = {
      platform: form.platform,
      amount: parseInt(form.amount) || 0,
      due_date: form.due_date,
      category: form.category || null,
      notes: form.notes || null,
      installment_current: null,
      installment_total: null,
    }
    try {
      if (editId) {
        await api(`/api/debts/${editId}`, { method: 'PATCH', body: JSON.stringify(data) })
      } else {
        await api('/api/debts', { method: 'POST', body: JSON.stringify(data) })
      }
      setShowForm(false)
      setEditId(null)
      setForm({ platform: '', amount: '', due_date: '', category: '', notes: '' })
      load()
    } catch (e: any) { setError(e.message || 'Gagal simpan.') }
  }

  function openEdit(d: DebtResponse) {
    setEditId(d.id)
    setForm({ platform: d.platform, amount: String(d.amount), due_date: d.due_date, category: d.category || '', notes: d.notes || '' })
    setShowForm(true)
  }

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 bg-background/80 backdrop-blur-sm border-b z-30">
          <div className="flex items-center justify-between p-4 lg:px-8">
            <h1 className="text-xl font-semibold">Utang</h1>
            <div className="flex items-center gap-3">
              <Button onClick={() => { setEditId(null); setForm({ platform: '', amount: '', due_date: '', category: '', notes: '' }); setShowForm(!showForm) }} size="sm">
                <Plus className="w-4 h-4 mr-1" /> Tambah
              </Button>
              <MobileNav />
            </div>
          </div>
        </header>

        <div className="p-4 lg:p-8 animate-fade-in">
          {celebration && (
            <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none" onClick={() => setCelebration(null)}>
              {Array.from({ length: 30 }).map((_, i) => (
                <div key={i} className="absolute w-2 h-2 rounded-full" style={{
                  left: Math.random() * 100 + '%',
                  top: Math.random() * 100 + '%',
                  backgroundColor: ['#22c55e','#3b82f6','#eab308','#ec4899','#8b5cf6','#14b8a6'][Math.floor(Math.random() * 6)],
                  transform: 'scale(' + (Math.random() * 2 + 0.5) + ')',
                }} />
              ))}
              <div className="bg-white rounded-2xl shadow-2xl p-8 text-center max-w-sm mx-4 pointer-events-auto animate-fade-in border-2 border-emerald-200" onClick={e => e.stopPropagation()}>
                <div className="text-5xl mb-4">{['🎉','🥳','🏆','⭐','🚀','💪'][Math.floor(Math.random()*6)]}</div>
                <h2 className="text-2xl font-bold text-emerald-700 mb-2">
                  {['SELAMAT! Kamu sudah melunasi utang!','LUNAS! Mantap!','Keren! Utang lunas!','Yes! Satu lagi beres!','Selamat! Kamu hebat!'][Math.floor(Math.random()*5)]}
                </h2>
                <p className="text-muted-foreground mb-1"><strong>{celebration.platform}</strong> — sudah lunas!</p>
                <p className="text-sm text-muted-foreground">Total utang lunas: {celebration.count}</p>
                <button onClick={() => setCelebration(null)} className="mt-4 px-6 h-10 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">Tutup</button>
              </div>
            </div>
          )}

          {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-sm text-red-700">{error}</div>}

          {/* OCR Upload */}
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-8 cursor-pointer transition-colors hover:border-accent hover:bg-accent/5"
                onDragOver={(e) => e.preventDefault()}
                onDrop={async (e) => {
                  e.preventDefault()
                  const file = e.dataTransfer.files?.[0]
                  if (!file || !file.type.startsWith('image/')) return
                  setOcrLoading(true); setError(null)
                  try {
                    const fd = new FormData(); fd.append('file', file)
                    const res = await fetch(API + '/api/ocr', { method: 'POST', headers: token() ? { Authorization: 'Bearer ' + token() } : {}, body: fd })
                    if (!res.ok) throw new Error(await res.text())
                    setOcrPreview((await res.json()).parsed)
                  } catch (e) { setError('OCR gagal') }
                  setOcrLoading(false)
                }}
                onClick={() => document.getElementById('ocr-input')?.click()}
              >
                <Upload className="w-10 h-10 text-muted-foreground/50 mb-3" />
                <p className="font-medium text-sm">{ocrLoading ? 'Memproses...' : 'Upload screenshot tagihan'}</p>
                <p className="text-xs text-muted-foreground mt-1">Atau klik untuk pilih file</p>
              </div>
              <input id="ocr-input" type="file" accept="image/*" className="hidden"
                onChange={async (e) => {
                  const file = e.target.files?.[0]
                  if (!file) return
                  setOcrLoading(true); setError(null)
                  try {
                    const fd = new FormData(); fd.append('file', file)
                    const res = await fetch(API + '/api/ocr', { method: 'POST', headers: token() ? { Authorization: 'Bearer ' + token() } : {}, body: fd })
                    if (!res.ok) throw new Error(await res.text())
                    setOcrPreview((await res.json()).parsed)
                  } catch { setError('OCR gagal') }
                  setOcrLoading(false)
                }}
              />

              {ocrPreview && (
                <div className="mt-4 p-3 bg-secondary rounded-lg text-sm space-y-1">
                  <p><b>Platform:</b> {ocrPreview.platform || '?'}</p>
                  <p><b>Jumlah:</b> {ocrPreview.amount ? `Rp${ocrPreview.amount.toLocaleString('id-ID')}` : '?'}</p>
                  <p><b>Jatuh tempo:</b> {ocrPreview.due_date || '?'}</p>
                  {ocrPreview.installment_current && ocrPreview.installment_total &&
                    <p><b>Cicilan:</b> {ocrPreview.installment_current}/{ocrPreview.installment_total}</p>}
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" onClick={async () => {
                      try {
                        await api('/api/debts', {
                          method: 'POST',
                          body: JSON.stringify({
                            platform: ocrPreview.platform || 'Tagihan',
                            amount: ocrPreview.amount || 0,
                            due_date: ocrPreview.due_date || new Date().toISOString().split('T')[0],
                            category: ocrPreview.category || null,
                            notes: ocrPreview.notes || null,
                            installment_current: ocrPreview.installment_current || null,
                            installment_total: ocrPreview.installment_total || null,
                          }),
                        })
                        setOcrPreview(null)
                        load()
                      } catch (e: any) { setError(e.message || 'Gagal simpan') }
                    }}>✅ Simpan</Button>
                    <Button size="sm" variant="outline" onClick={() => setOcrPreview(null)}>❌ Batal</Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Add/Edit Form */}
          {showForm && (
            <Card className="mb-6">
              <CardContent className="p-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
                  <input value={form.platform} onChange={e => setForm({...form, platform: e.target.value})} placeholder="Platform" className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                  <input value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="Jumlah (Rp)" type="number" className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                  <input value={form.due_date} onChange={e => setForm({...form, due_date: e.target.value})} placeholder="Jatuh tempo (YYYY-MM-DD)" className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                  <input value={form.category} onChange={e => setForm({...form, category: e.target.value})} placeholder="Kategori" className="h-10 rounded-lg border border-input bg-background px-3 text-sm" />
                  <input value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="Catatan" className="h-10 rounded-lg border border-input bg-background px-3 text-sm sm:col-span-2" />
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleSave} size="sm">{editId ? 'Simpan' : 'Tambah'}</Button>
                  <Button onClick={() => { setShowForm(false); setEditId(null) }} variant="outline" size="sm">Batal</Button>
                </div>
              </CardContent>
            </Card>
          )}

          <Card className="overflow-hidden">
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <CardTitle>Daftar Utang</CardTitle>
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <input placeholder="Cari platform..." value={filter} onChange={e => setFilter(e.target.value)} className="h-9 w-40 lg:w-56 rounded-lg border border-input bg-background pl-9 pr-3 text-sm" />
                  </div>
                  <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="h-9 rounded-lg border border-input bg-background px-3 text-sm">
                    <option value="">Semua</option>
                    <option value="active">Aktif</option>
                    <option value="paid">Lunas</option>
                    <option value="late">Terlambat</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? <div className="space-y-3">{[1,2,3,4,5].map(i => <div key={i} className="h-14 bg-secondary rounded-lg animate-pulse" />)}</div>
              : <>
                  {/* Active Debts */}
                  {activeDebts.length === 0 && paidDebts.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">Belum ada utang.</div>
                  ) : activeDebts.length > 0 ? (
                    <div>
                      {activeDebts.length > 0 && paidDebts.length > 0 && (
                        <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">Aktif</h3>
                      )}
                      {/* Mobile: Card list */}
                      <div className="space-y-3 lg:hidden">
                        {activeDebts.map(d => (
                          <div key={d.id} className="border rounded-xl p-4 space-y-3">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Badge variant={statusVariant[d.status] || 'default'}>{d.status === 'active' ? 'Aktif' : 'Terlambat'}</Badge>
                                <span className="font-semibold">{d.platform}</span>
                              </div>
                              <span className="font-bold">Rp{d.amount.toLocaleString('id-ID')}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm text-muted-foreground">
                              <span>Jatuh tempo {d.due_date}</span>
                              {d.installment_current && d.installment_total && <span>{d.installment_current}/{d.installment_total}</span>}
                            </div>
                            {d.category && <p className="text-xs text-muted-foreground">{d.category}</p>}
                            <div className="flex items-center gap-2 pt-1 border-t">
                              <button onClick={() => handleStatus(d.id, 'paid', d.platform)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-emerald-100 text-emerald-600" title="Lunas"><Check className="w-5 h-5" /></button>
                              <button onClick={() => handleStatus(d.id, 'late', d.platform)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-red-100 text-red-600" title="Terlambat"><AlertTriangle className="w-5 h-5" /></button>
                              <button onClick={() => openEdit(d)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-blue-100 text-blue-600" title="Edit"><Pencil className="w-5 h-5" /></button>
                              <button onClick={() => handleDelete(d.id)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-red-100 text-red-600" title="Hapus"><Trash2 className="w-5 h-5" /></button>
                            </div>
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
                              <th className="pb-3 font-medium">Kategori</th>
                              <th className="pb-3 font-medium">Aksi</th>
                            </tr>
                          </thead>
                          <tbody>
                            {activeDebts.map(d => (
                              <tr key={d.id} className="border-b last:border-0 hover:bg-secondary/30 transition-colors">
                                <td className="py-3"><Badge variant={statusVariant[d.status] || 'default'}>{d.status === 'active' ? 'Aktif' : 'Terlambat'}</Badge></td>
                                <td className="py-3 font-medium">{d.platform}</td>
                                <td className="py-3 font-semibold">Rp{d.amount.toLocaleString('id-ID')}</td>
                                <td className="py-3 text-sm text-muted-foreground">{d.due_date}</td>
                                <td className="py-3 text-sm text-muted-foreground">{d.installment_current && d.installment_total ? `${d.installment_current}/${d.installment_total}` : '-'}</td>
                                <td className="py-3 text-sm text-muted-foreground">{d.category || '-'}</td>
                                <td className="py-3">
                                  <div className="flex items-center gap-1">
                                    <button onClick={() => handleStatus(d.id, 'paid', d.platform)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-emerald-100 text-emerald-600" title="Lunas"><Check className="w-5 h-5" /></button>
                                    <button onClick={() => handleStatus(d.id, 'late', d.platform)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-red-100 text-red-600" title="Terlambat"><AlertTriangle className="w-5 h-5" /></button>
                                    <button onClick={() => openEdit(d)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-blue-100 text-blue-600" title="Edit"><Pencil className="w-5 h-5" /></button>
                                    <button onClick={() => handleDelete(d.id)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-red-100 text-red-600" title="Hapus"><Trash2 className="w-5 h-5" /></button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : null}

                  {/* Paid Debts */}
                  {paidDebts.length > 0 && (
                    <div className={activeDebts.length > 0 ? 'mt-8' : ''}>
                      <h3 className="text-sm font-semibold text-emerald-600 mb-3 uppercase tracking-wider flex items-center gap-2">
                        ✅ Lunas ({paidDebts.length})
                      </h3>
                      {/* Mobile: Card list */}
                      <div className="space-y-3 lg:hidden">
                        {paidDebts.map(d => (
                          <div key={d.id} className="border border-emerald-200 rounded-xl p-4 space-y-3 bg-emerald-50/30">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Badge variant="paid">Lunas</Badge>
                                <span className="font-semibold">{d.platform}</span>
                              </div>
                              <span className="font-bold">Rp{d.amount.toLocaleString('id-ID')}</span>
                            </div>
                            <div className="text-sm text-muted-foreground">Jatuh tempo {d.due_date}</div>
                            <div className="flex items-center gap-2 pt-1 border-t border-emerald-200">
                              <button onClick={() => handleStatus(d.id, 'active', d.platform)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-amber-100 text-amber-600" title="Aktifkan kembali"><Check className="w-5 h-5" /></button>
                              <button onClick={() => handleDelete(d.id)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-red-100 text-red-600" title="Hapus"><Trash2 className="w-5 h-5" /></button>
                            </div>
                          </div>
                        ))}
                      </div>
                      {/* Desktop: Table */}
                      <div className="hidden lg:block overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b text-left text-sm text-emerald-600">
                              <th className="pb-3 font-medium">Platform</th>
                              <th className="pb-3 font-medium">Jumlah</th>
                              <th className="pb-3 font-medium">Jatuh Tempo</th>
                              <th className="pb-3 font-medium">Aksi</th>
                            </tr>
                          </thead>
                          <tbody>
                            {paidDebts.map(d => (
                              <tr key={d.id} className="border-b last:border-0">
                                <td className="py-3 font-medium">{d.platform}</td>
                                <td className="py-3 font-semibold">Rp{d.amount.toLocaleString('id-ID')}</td>
                                <td className="py-3 text-sm text-muted-foreground">{d.due_date}</td>
                                <td className="py-3">
                                  <div className="flex items-center gap-1">
                                    <button onClick={() => handleStatus(d.id, 'active', d.platform)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-amber-100 text-amber-600" title="Aktifkan kembali"><Check className="w-5 h-5" /></button>
                                    <button onClick={() => handleDelete(d.id)} className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-red-100 text-red-600" title="Hapus"><Trash2 className="w-5 h-5" /></button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </>
              }
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
