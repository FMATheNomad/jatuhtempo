'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useEffect, useState } from 'react'
import {
  LayoutDashboard, CreditCard, Settings, History, LogOut, TrendingDown,
  Calendar, Bell, Shield, Sun, Moon,
} from 'lucide-react'
import { useTheme } from '@/components/theme-provider'

const commonLinks = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/debts', label: 'Utang', icon: CreditCard },
  { href: '/monthly', label: 'Bulanan', icon: Calendar },
  { href: '/upcoming', label: 'Akan Datang', icon: Bell },
  { href: '/strategy', label: 'Strategi', icon: TrendingDown },
  { href: '/history', label: 'Riwayat', icon: History },
  { href: '/settings', label: 'Pengaturan', icon: Settings },
]

const adminLink = { href: '/admin/rates', label: 'Admin Rates', icon: Shield }

export function Sidebar() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('session_token')
    if (!token) { setIsAdmin(false); return }
    fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => setIsAdmin(data?.is_admin === true))
      .catch(() => setIsAdmin(false))
    // TODO: Share admin state with MobileNav via React Context to avoid double API call
  }, [])

  const links = isAdmin ? [...commonLinks, adminLink] : commonLinks

  return (
    <aside className="hidden lg:flex lg:flex-col w-64 border-r bg-card h-screen sticky top-0">
      <div className="p-6 border-b">
        <Link href="/" className="flex items-center gap-2">
          <img src="/assets/logo.webp" alt="JatuhTempo" className="h-8 w-auto" />
        </Link>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                active
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t space-y-1">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-all w-full"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {theme === 'dark' ? 'Mode Terang' : 'Mode Gelap'}
        </button>
        <button
          onClick={async () => {
            const token = localStorage.getItem('session_token')
            if (token) await fetch('/api/auth/logout', { method: 'POST', headers: { Authorization: `Bearer ${token}` } }).catch(() => {})
            localStorage.removeItem('session_token'); window.location.href = '/'
          }}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-all w-full"
        >
          <LogOut className="w-4 h-4" />
          Keluar
        </button>
      </div>
    </aside>
  )
}
