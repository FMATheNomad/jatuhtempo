'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard, CreditCard, Settings, History, LogOut,
} from 'lucide-react'

const links = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/debts', label: 'Utang', icon: CreditCard },
  { href: '/history', label: 'Riwayat', icon: History },
  { href: '/settings', label: 'Pengaturan', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden lg:flex lg:flex-col w-64 border-r bg-card h-screen sticky top-0">
      <div className="p-6 border-b">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg gradient-card flex items-center justify-center">
            <span className="text-white font-bold text-sm">JT</span>
          </div>
          <span className="font-semibold text-lg">JatuhTempo</span>
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

      <div className="p-4 border-t">
        <button
          onClick={() => { localStorage.removeItem('session_token'); window.location.href = '/' }}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-all w-full"
        >
          <LogOut className="w-4 h-4" />
          Keluar
        </button>
      </div>
    </aside>
  )
}
