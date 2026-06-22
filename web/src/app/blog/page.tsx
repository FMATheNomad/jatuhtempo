'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Calendar, ArrowLeft, Sparkles } from 'lucide-react'

interface BlogPost {
  pillar: string
  title: string
  content: string
  generated_at: string
  source: string
  posted: boolean
}

export default function BlogPage() {
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<BlogPost | null>(null)

  useEffect(() => {
    fetch('/api/blog')
      .then(r => r.json())
      .then(d => setPosts(d.posts || []))
      .catch(() => setPosts([]))
      .finally(() => setLoading(false))
  }, [])

  const typeIcon: Record<string, string> = { edukasi: '📚', data: '📊', psikologi: '🧠', produk: '⚡' }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="max-w-3xl mx-auto px-4 py-12 animate-fade-in">
        <Link href="/" className="inline-flex items-center gap-1 text-sm text-accent hover:underline mb-8">
          <ArrowLeft className="w-4 h-4" /> Kembali ke Beranda
        </Link>

        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Blog JatuhTempo</h1>
        <p className="text-slate-500 dark:text-slate-400 mb-8">Tips, strategi, dan wawasan seputar manajemen utang.</p>

        {selected ? (
          <div className="animate-fade-in">
            <button onClick={() => setSelected(null)} className="text-sm text-accent hover:underline mb-4 inline-flex items-center gap-1">
              <ArrowLeft className="w-4 h-4" /> Kembali ke daftar
            </button>
            <article className="bg-white dark:bg-card border border-border rounded-2xl p-6 lg:p-8">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4">
                <span>{typeIcon[selected.pillar] || '📄'} {selected.pillar}</span>
                <span>·</span>
                <Calendar className="w-3 h-3" />
                <span>{new Date(selected.generated_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">{selected.title}</h2>
              <div className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line text-sm">{selected.content}</div>
            </article>
          </div>
        ) : (
          <>
            {loading ? (
              <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="h-32 bg-secondary rounded-2xl animate-pulse" />)}</div>
            ) : posts.length === 0 ? (
              <div className="text-center py-16 text-muted-foreground">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>Belum ada artikel. Konten akan muncul setelah AI agent mulai generate.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {posts.map((post, i) => (
                  <button key={i} onClick={() => setSelected(post)} className="w-full text-left bg-white dark:bg-card border border-border rounded-2xl p-5 hover:border-accent/50 transition-all hover:shadow-sm">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                      <span>{typeIcon[post.pillar] || '📄'} {post.pillar}</span>
                      <span>·</span>
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(post.generated_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long' })}</span>
                    </div>
                    <h2 className="font-semibold text-slate-900 dark:text-white mb-1">{post.title}</h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2">{post.content.replace(/<[^>]+>/g, '').slice(0, 150)}...</p>
                  </button>
                ))}
              </div>
            )}
          </>
        )}

        <div className="mt-12 text-center text-xs text-muted-foreground">
          Konten digenerate otomatis oleh AI setiap 6 jam. <a href="/" className="text-accent hover:underline">Kembali ke Beranda</a>
        </div>
      </div>
    </div>
  )
}
