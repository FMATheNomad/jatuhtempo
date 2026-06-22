import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'

const inter = Inter({ subsets: ['latin'] })

const baseUrl = 'https://jatuhtempo.up.railway.app'

export const metadata: Metadata = {
  title: 'JatuhTempo Beta — Kelola Utang dengan AI',
  description: 'Aplikasi manajemen utang berbasis AI untuk Indonesia. Catat utang, scan tagihan otomatis dengan AI, dapatkan reminder Telegram, dan strategi bebas utang. Gratis.',
  keywords: ['manajemen utang', 'aplikasi utang', 'tracking utang', 'debt management', 'pinjol', 'paylater', 'Indonesia', 'OCR tagihan', 'JatuhTempo'],
  icons: { icon: '/favicon.png' },
  openGraph: {
    title: 'JatuhTempo — Kelola Utang dengan AI',
    description: 'Catat utang, scan tagihan otomatis, reminder Telegram, strategi bebas utang. Gratis untuk Indonesia.',
    url: baseUrl,
    siteName: 'JatuhTempo',
    locale: 'id_ID',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'JatuhTempo — Kelola Utang dengan AI',
    description: 'Catat utang, scan tagihan otomatis, reminder Telegram, strategi bebas utang. Gratis.',
  },
  robots: {
    index: true,
    follow: true,
  },
  alternates: {
    canonical: baseUrl,
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
