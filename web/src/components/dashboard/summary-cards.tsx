'use client'

import { Card, CardContent } from '@/components/ui/card'
import { CreditCard, TrendingUp, Clock, AlertTriangle } from 'lucide-react'

interface Summary {
  total_active: number
  total_amount: number
  paid_this_month: number
  paid_amount: number
  upcoming: { id: string; due_date: string }[]
}

const cards = [
  {
    label: 'Utang Aktif',
    key: 'total_active' as const,
    suffix: '',
    icon: CreditCard,
    gradient: 'from-blue-500 to-blue-600',
  },
  {
    label: 'Total Amount',
    key: 'total_amount' as const,
    prefix: 'Rp',
    format: true,
    icon: TrendingUp,
    gradient: 'from-emerald-500 to-emerald-600',
  },
  {
    label: 'Lunas Bulan Ini',
    key: 'paid_this_month' as const,
    suffix: '',
    icon: Clock,
    gradient: 'from-violet-500 to-violet-600',
  },
  {
    label: 'Mendatang',
    key: 'upcoming' as const,
    suffix: 'tagihan',
    icon: AlertTriangle,
    gradient: 'from-amber-500 to-amber-600',
  },
]

export function SummaryCards({ summary }: { summary: Summary }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map(({ label, key, prefix, suffix, format, icon: Icon, gradient }) => {
        let value: string | number = (key === 'upcoming')
          ? summary.upcoming.length
          : (summary[key] as number)
        if (format) value = `Rp${(value as number).toLocaleString('id-ID')}`
        if (prefix && !format) value = `${prefix}${value}`
        if (suffix) value = `${value} ${suffix}`

        return (
          <Card key={key} className="card-hover overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-muted-foreground font-medium">{label}</span>
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-sm`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
              </div>
              <p className="text-2xl font-bold tracking-tight">{value}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
