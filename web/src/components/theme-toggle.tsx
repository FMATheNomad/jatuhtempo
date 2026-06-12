'use client'

import { useTheme } from './theme-provider'
import { Sun, Moon, Monitor } from 'lucide-react'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  const cycle = () => {
    if (theme === 'light') setTheme('dark')
    else if (theme === 'dark') setTheme('system')
    else setTheme('light')
  }

  return (
    <button
      onClick={cycle}
      className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-secondary transition-colors"
      title={theme === 'light' ? 'Mode Terang' : theme === 'dark' ? 'Mode Gelap' : 'Ikuti Sistem'}
    >
      {theme === 'light' ? <Sun className="w-5 h-5" /> : theme === 'dark' ? <Moon className="w-5 h-5" /> : <Monitor className="w-5 h-5" />}
    </button>
  )
}
