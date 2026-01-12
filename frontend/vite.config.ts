import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // load .env files for the current mode (development, production, etc.)
  const env = loadEnv(mode, process.cwd(), '')

  // Use explicit Vite env variables to control proxy target
  // - Set VITE_API_URL to a full URL to use that target (e.g. http://localhost:8000)
  // - Or set VITE_USE_LOCAL=true to proxy to local http://localhost:8000
  const apiUrlFromEnv = env.VITE_API_URL?.trim()
  const useLocal = (env.VITE_USE_LOCAL || '').toLowerCase() === 'true'
  const defaultProd = 'https://preconleague.cs.house'
  const target = apiUrlFromEnv || (useLocal ? 'http://localhost:8000' : defaultProd)
  const secure = target.startsWith('https')

  return {
    plugins: [react()],
    base: '/PreconLeague/',
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          secure,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  }
})
