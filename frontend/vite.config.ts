import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/PreconLeague/',
  server: {
    port: 5173,
    proxy: {
      // Proxy /api/* to your OKD-hosted FastAPI during development. The
      // rewrite removes the /api prefix so a request to /api/decks/ will be
      // forwarded to https://preconleague.cs.house/decks/
      '/api': {
        target: 'https://preconleague.cs.house',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
