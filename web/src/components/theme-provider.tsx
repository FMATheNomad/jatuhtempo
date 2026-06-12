'use client'

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

const ThemeContext = createContext<{
  theme: Theme
  resolved: 'light' | 'dark'
  setTheme: (t: Theme) => void
}>({ theme: 'system', resolved: 'light', setTheme: () => {} })

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('system')
  const [resolved, setResolved] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const stored = localStorage.getItem('theme') as Theme | null
    if (stored) setThemeState(stored)
  }, [])

  useEffect(() => {
    localStorage.setItem('theme', theme)
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const update = () => {
      const isDark = theme === 'dark' || (theme === 'system' && mq.matches)
      setResolved(isDark ? 'dark' : 'light')
      document.documentElement.classList.toggle('dark', isDark)
    }
    update()
    mq.addEventListener('change', update)
    return () => mq.removeEventListener('change', update)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, resolved, setTheme: setThemeState }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
