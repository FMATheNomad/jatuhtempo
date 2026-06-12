'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useEffect, useState } from 'react'
import { LayoutDashboard, CreditCard, History, Settings, TrendingDown, Calendar, Bell, Shield, Menu, X, LogOut } from 'lucide-react'

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

export function MobileNav() {
  const [open, setOpen] = useState(false)
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)
  const pathname = usePathname()

  useEffect(() => {
    const token = localStorage.getItem('session_token')
    if (!token) { setIsAdmin(false); return }
    fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => setIsAdmin(data?.is_admin === true))
      .catch(() => setIsAdmin(false))
    // TODO: Share admin state with Sidebar via React Context to avoid double API call
  }, [])

  const links = isAdmin ? [...commonLinks, adminLink] : commonLinks

  return (
    <div className="lg:hidden">
      <button onClick={() => setOpen(!open)} className="min-h-[44px] min-w-[44px] flex items-center justify-center hover:bg-secondary rounded-lg">
        {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setOpen(false)} />
          <div className="fixed top-14 left-0 right-0 bg-card border-b z-50 p-4 shadow-lg animate-fade-in">
            <nav className="space-y-1">
              {links.map(({ href, label, icon: Icon }) => {
                const active = pathname === href || (href !== '/' && pathname.startsWith(href))
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={() => setOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-4 min-h-[44px] rounded-lg text-sm font-medium transition-all",
                      active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-secondary"
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </Link>
                )
              })}
            </nav>
            <hr className="my-2 border-border" />
            <button
              onClick={() => { localStorage.removeItem('session_token'); window.location.href = '/' }}
              className="flex items-center gap-3 px-4 min-h-[44px] w-full rounded-lg text-sm font-medium text-muted-foreground hover:bg-secondary transition-all"
            >
              <LogOut className="w-4 h-4" />
              Keluar
            </button>
          </div>
        </>
      )}
    </div>
  )
}
