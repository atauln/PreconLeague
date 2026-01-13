// Runtime configuration helper.
// It prefers a runtime-injected global `__RUNTIME__` (e.g. served from
// /runtime-config.js) and falls back to Vite's build-time env vars.

const win = typeof window !== 'undefined' ? (window as any) : undefined
const runtime = win && win.__RUNTIME__ ? win.__RUNTIME__ : {}

export const runtimeApiUrl: string = runtime.VITE_API_URL || (import.meta.env.VITE_API_URL as string) || ''

export function apiUrl(path: string) {
  return runtimeApiUrl ? `${runtimeApiUrl}${path}` : `/api${path}`
}

export function getRuntimeInfo() {
  return {
    runtimeApiUrl,
    viteApi: (import.meta.env.VITE_API_URL as string) || '',
    useLocal: ((import.meta.env.VITE_USE_LOCAL as string) || '').toLowerCase() === 'true',
    baseUrl: (import.meta.env.BASE_URL as string) || '/',
  }
}
