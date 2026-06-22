'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Calendar, ArrowLeft, Sparkles, Check } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface BlogPost {
  pillar: string
  title: string
  content: string
  generated_at: string
  source: string
  posted: boolean
}

const PILLARS = [
  { key: 'all', label: 'Semua', icon: '📋' },
  { key: 'edukasi', label: 'Edukasi', icon: '📚' },
  { key: 'data', label: 'Data & Riset', icon: '📊' },
  { key: 'ekonomi', label: 'Ekonomi', icon: '📈' },
  { key: 'psikologi', label: 'Psikologi', icon: '🧠' },
  { key: 'teknologi', label: 'Teknologi', icon: '💻' },
  { key: 'gaya-hidup', label: 'Gaya Hidup', icon: '💪' },
]

const PILLAR_COLORS: Record<string, string> = {
  edukasi: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400',
  data: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-400',
  ekonomi: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',
  psikologi: 'bg-pink-100 text-pink-700 dark:bg-pink-900/40 dark:text-pink-400',
  teknologi: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-400',
  'gaya-hidup': 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400',
}

export default function BlogPage() {
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<BlogPost | null>(null)
  const [copied, setCopied] = useState(false)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetch('/api/blog')
      .then(r => r.json())
      .then(d => setPosts(d.posts || []))
      .catch(() => setPosts([]))
      .finally(() => setLoading(false))
  }, [])

  const filtered = filter === 'all' ? posts : posts.filter(p => p.pillar === filter)

  if (selected) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
        <div className="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
          <button onClick={() => setSelected(null)} className="inline-flex items-center gap-1 text-sm text-accent hover:underline mb-8">
            <ArrowLeft className="w-4 h-4" /> Kembali ke daftar
          </button>

          <article className="bg-white dark:bg-card border border-border rounded-2xl overflow-hidden">
            <div className="p-8 lg:p-10">
              <div className="flex items-center gap-3 text-xs text-muted-foreground mb-4">
                <span className={`px-2 py-0.5 rounded-full font-medium ${PILLAR_COLORS[selected.pillar] || ''}`}>
                  {PILLARS.find(p => p.key === selected.pillar)?.icon} {PILLARS.find(p => p.key === selected.pillar)?.label || selected.pillar}
                </span>
                <span>·</span>
                <Calendar className="w-3 h-3" />
                <span>{new Date(selected.generated_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                <span>·</span>
                <span>{selected.source}</span>
              </div>
              <h1 className="text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">{selected.title}</h1>
              <div className="prose prose-slate dark:prose-invert max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{selected.content}</ReactMarkdown>
              </div>
              {/* Share */}
              <div className="flex items-center gap-3 mt-10 pt-6 border-t border-border">
                <span className="text-xs text-muted-foreground">Bagikan:</span>
                <button onClick={() => {
                  window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(selected.title + '\n\nhttps://jatuhtempo.up.railway.app/blog')}`, '_blank', 'noopener')
                }} className="min-h-[36px] px-3 flex items-center justify-center rounded-lg hover:bg-sky-100 dark:hover:bg-sky-900/30 text-sky-600 transition-colors text-sm font-medium">
                  𝕏
                </button>
                <button onClick={() => {
                  window.open(`https://wa.me/?text=${encodeURIComponent(selected.title + '\n\nhttps://jatuhtempo.up.railway.app/blog')}`, '_blank', 'noopener')
                }} className="min-h-[36px] px-3 flex items-center justify-center rounded-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/30 text-emerald-600 transition-colors text-sm font-medium">
                  WA
                </button>
                <button onClick={() => {
                  navigator.clipboard.writeText('https://jatuhtempo.up.railway.app/blog')
                  setCopied(true)
                  setTimeout(() => setCopied(false), 2000)
                }} className="min-h-[36px] px-3 flex items-center justify-center rounded-lg hover:bg-secondary transition-colors text-sm font-medium text-muted-foreground">
                  {copied ? <Check className="w-4 h-4 text-emerald-500" /> : '📋 Salin link'}
                </button>
              </div>
            </div>
          </article>

          <div className="mt-8 text-center">
            <Link href="/" className="text-sm text-accent hover:underline">← Kembali ke Beranda</Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="max-w-5xl mx-auto px-4 py-12 animate-fade-in">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Blog JatuhTempo</h1>
          <Link href="/" className="text-sm text-accent hover:underline hidden sm:inline">← Beranda</Link>
        </div>
        <p className="text-slate-500 dark:text-slate-400 mb-8">Tips, wawasan, dan data seputar keuangan dan utang dari Tim Riset JatuhTempo.</p>

        {/* Pillar filter tabs */}
        <div className="flex flex-wrap gap-2 mb-8">
          {PILLARS.map(p => (
            <button key={p.key} onClick={() => setFilter(p.key)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                filter === p.key
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'bg-white dark:bg-card border border-border text-muted-foreground hover:bg-secondary'
              }`}
            >
              {p.icon} {p.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1,2,3,4,5,6].map(i => <div key={i} className="h-44 bg-secondary rounded-2xl animate-pulse" />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <p>Belum ada artikel di kategori ini.</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((post, i) => (
              <button key={i} onClick={() => setSelected(post)}
                className="text-left bg-white dark:bg-card border border-border rounded-2xl p-5 hover:border-accent/50 hover:shadow-sm transition-all group"
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${PILLAR_COLORS[post.pillar] || ''}`}>
                    {PILLARS.find(p => p.key === post.pillar)?.icon} {PILLARS.find(p => p.key === post.pillar)?.label || post.pillar}
                  </span>
                  <span className="text-[11px] text-muted-foreground">{new Date(post.generated_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })}</span>
                </div>
                <h2 className="font-semibold text-slate-900 dark:text-white text-sm mb-2 line-clamp-2 group-hover:text-accent transition-colors">{post.title}</h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{post.content.replace(/<[^>]+>/g, '').replace(/[#*\[\]]/g, '').slice(0, 120)}...</p>
              </button>
            ))}
          </div>
        )}

        <div className="mt-12 pt-8 border-t border-border text-center">
          <p className="text-xs text-muted-foreground mb-2">Artikel baru setiap 6 jam oleh Tim Riset JatuhTempo</p>
          <Link href="/" className="text-sm text-accent hover:underline">← Kembali ke Beranda</Link>
        </div>
      </div>
    </div>
  )
}
