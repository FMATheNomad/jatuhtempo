'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { LayoutDashboard, CreditCard, History, Settings, Menu, X } from 'lucide-react'
import { useState } from 'react'

const links = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/debts', label: 'Utang', icon: CreditCard },
  { href: '/history', label: 'Riwayat', icon: History },
  { href: '/settings', label: 'Pengaturan', icon: Settings },
]

export function MobileNav() {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()

  return (
    <div className="lg:hidden">
      <button onClick={() => setOpen(!open)} className="p-2 hover:bg-secondary rounded-lg">
        {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setOpen(false)} />
          <div className="fixed bottom-0 left-0 right-0 bg-card rounded-t-2xl border-t z-50 p-4 pb-8 animate-slide-in">
            <nav className="space-y-1">
              {links.map(({ href, label, icon: Icon }) => {
                const active = pathname === href || (href !== '/' && pathname.startsWith(href))
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={() => setOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
                      active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-secondary"
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </Link>
                )
              })}
            </nav>
          </div>
        </>
      )}
    </div>
  )
}
