import { Container, Typography, Box, Paper } from '@mui/material'

export default function Admin() {
  // Vite exposes env vars via import.meta.env
  const viteApi = (import.meta.env.VITE_API_URL as string) || ''
  const useLocal = ((import.meta.env.VITE_USE_LOCAL as string) || '').toLowerCase() === 'true'
  const baseUrl = (import.meta.env.BASE_URL as string) || '/'

  // Compute the target the app will use (matches vite.config logic)
  const defaultProd = 'https://preconleague-api.cs.house'
  const target = viteApi || (useLocal ? 'http://localhost:8000' : defaultProd)

  // Print to console at admin render for easy debugging in dev tools
  console.info('[PreconLeague] Runtime debug: VITE_API_URL=', viteApi)
  console.info('[PreconLeague] Runtime debug: VITE_USE_LOCAL=', useLocal)
  console.info('[PreconLeague] Computed API target=', target)

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>Admin / Runtime Info</Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box>
          <Typography><strong>import.meta.env.VITE_API_URL</strong>: {viteApi || '<empty>'}</Typography>
          <Typography><strong>import.meta.env.VITE_USE_LOCAL</strong>: {String(useLocal)}</Typography>
          <Typography><strong>import.meta.env.BASE_URL</strong>: {baseUrl}</Typography>
          <Typography><strong>Computed API target</strong>: {target}</Typography>
          <Typography><strong>Window location</strong>: {typeof window !== 'undefined' ? window.location.href : ''}</Typography>
        </Box>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1">Notes</Typography>
        <Typography color="text.secondary">If VITE_API_URL is empty and VITE_USE_LOCAL is not true, the app will call the production API at https://preconleague-api.cs.house. In development the Vite server proxies `/api` to the target defined in `vite.config.ts`.</Typography>
      </Paper>
    </Container>
  )
}
