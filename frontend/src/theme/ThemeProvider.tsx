import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { ThemeProvider as MuiThemeProvider, createTheme, CssBaseline } from '@mui/material'
import ThemeToggle from '../ThemeToggle'

type Mode = 'light' | 'dark'

const COOKIE_NAME = 'pl_theme'

function setCookie(name: string, value: string, days = 365) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString()
  let cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`
  if (location.protocol === 'https:') cookie += '; Secure'
  document.cookie = cookie
}

function getCookie(name: string) {
  const m = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return m ? decodeURIComponent(m[2]) : null
}

const ColorModeContext = createContext({ mode: null as Mode | null, toggleMode: () => {} })

export function useColorMode() {
  return useContext(ColorModeContext)
}

export const CustomThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<Mode | null>(null)

  useEffect(() => {
    // on mount, read localStorage, then cookie, then system preference
    try {
      const ls = localStorage.getItem(COOKIE_NAME)
      if (ls === 'dark' || ls === 'light') {
        setMode(ls as Mode)
        return
      }
    } catch (e) {
      // ignore localStorage errors
    }
    const c = getCookie(COOKIE_NAME)
    if (c === 'dark' || c === 'light') {
      setMode(c as Mode)
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setMode('dark')
    } else {
      setMode('light')
    }
  }, [])

  useEffect(() => {
    if (mode === null) return // don't write until initial value is known
    // keep a data attribute on document element for non-MUI styles
    document.documentElement.setAttribute('data-theme', mode)
    setCookie(COOKIE_NAME, mode)
    try {
      localStorage.setItem(COOKIE_NAME, mode)
    } catch (e) {
      // ignore
    }
  }, [mode])

  const colorMode = useMemo(
    () => ({ mode, toggleMode: () => setMode((m) => (m === 'dark' ? 'light' : 'dark')) }),
    [mode],
  )

  const effectiveMode: Mode = mode ?? 'light'

  const theme = useMemo(() => createTheme({ palette: { mode: effectiveMode } }), [effectiveMode])

  return (
    <ColorModeContext.Provider value={colorMode}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
        <ThemeToggle />
      </MuiThemeProvider>
    </ColorModeContext.Provider>
  )
}

export default CustomThemeProvider
