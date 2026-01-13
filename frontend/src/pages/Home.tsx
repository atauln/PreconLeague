import React, { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Link as MuiLink,
} from '@mui/material'

interface Deck {
  deck_id: number
  user_id: number
  user_name?: string
  moxfield_deck_url?: string | null
  archidekt_deck_url?: string | null
  source: string
  deck_name: string
}
// Build API URL from Vite env var. We do NOT rely on Vite's dev proxy `/api`.
// Set `VITE_API_URL` at build time (or via build-arg) to the full API origin
// (e.g. `https://preconleague-api.cs.house`). If it's missing we'll fall back
// to `/api` but log a warning so this is explicit.
const remoteApi = (import.meta.env.VITE_API_URL as string) || ''
const apiUrl = (path: string) => {
  if (!remoteApi) {
    // Keep fallback for development convenience, but warn loudly.
    console.warn('[PreconLeague] VITE_API_URL is not set — falling back to /api (ensure you set VITE_API_URL at build time)')
    return `/api${path}`
  }
  // Ensure the remoteApi does not have a trailing slash
  const origin = remoteApi.endsWith('/') ? remoteApi.slice(0, -1) : remoteApi
  return `${origin}/api${path}`
}

export default function Home() {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [source, setSource] = useState<'moxfield' | 'archidekt'>('moxfield')
  const [deckUrl, setDeckUrl] = useState('')
  const [creating, setCreating] = useState(false)
  const [createMessage, setCreateMessage] = useState<string | null>(null)

  useEffect(() => {
    fetchDecks()
    // Log runtime API info to help debugging in environments where build-time envs are used
    const viteApi = (import.meta.env.VITE_API_URL as string) || ''
    const useLocal = ((import.meta.env.VITE_USE_LOCAL as string) || '').toLowerCase() === 'true'
    const defaultProd = 'https://preconleague-api.cs.house'
    const target = viteApi || (useLocal ? 'http://localhost:8000' : defaultProd)
    console.info('[PreconLeague] Home startup API target=', target)
  }, [])

  async function fetchDecks() {
    setLoading(true)
    setError(null)
    try {
  const res = await fetch(apiUrl('/decks/'))
      if (!res.ok) {
        throw new Error(`Failed to fetch decks: ${res.status} ${res.statusText}`)
      }
      const data = await res.json()
      setDecks(data || [])
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setCreating(true)
    setCreateMessage(null)
    try {
      const payload = { source, deck_url: deckUrl }
      const res = await fetch(apiUrl('/decks/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const errText = await res.text()
        throw new Error(`Create failed: ${res.status} ${res.statusText} - ${errText}`)
      }
      const data = await res.json()
      setCreateMessage(`Deck created with id ${data.deck_id}`)
      setDeckUrl('')
      // Refresh list
      fetchDecks()
    } catch (err: unknown) {
      setCreateMessage(`Error: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setCreating(false)
    }
  }

  return (
    <Container maxWidth={false} sx={{ py: 4, px: 2 }}>
      <Box mb={3}>
        <Typography variant="h5">Precon League — Home</Typography>
        <Typography color="text.secondary">Choose a deck to edit (this demo is unauthenticated — any user can open any deck).</Typography>
      </Box>

      <Box mb={4} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">All decks</Typography>
      </Box>

      {loading && <Box my={2}><CircularProgress /></Box>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {!loading && !error && (
        <Grid container spacing={0} sx={{ mb: 4 }}>
          {decks.length === 0 && (
            <Grid><Typography>No decks found.</Typography></Grid>
          )}
          {decks.map((d) => (
            <Grid sx={{ mb: 2 }} key={d.deck_id} style={{ width: '100%' }}>
              <Card >
                <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="subtitle1" noWrap>{d.deck_name}</Typography>
                    <Typography color="text.secondary">Owner: {d.user_name ?? d.user_id} • source: {d.source}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
                    {d.moxfield_deck_url && (
                      <MuiLink href={d.moxfield_deck_url} target="_blank" rel="noreferrer">View source</MuiLink>
                    )}
                    {d.archidekt_deck_url && (
                      <MuiLink href={d.archidekt_deck_url} target="_blank" rel="noreferrer">View source</MuiLink>
                    )}
                    <Button component={RouterLink} to={`/decks/${d.deck_id}`} variant="outlined">Edit</Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Box>
        <Typography variant="h6" sx={{ mb: 1 }}>Create or register a deck</Typography>
        <Typography color="text.secondary" sx={{ mb: 2 }}>Provide an Archidekt or Moxfield deck URL and click Submit to register it into the league.</Typography>

        <Box component="form" onSubmit={handleCreate} sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2 }}>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <FormControl sx={{ minWidth: 160 }}>
              <InputLabel id="source-label">Source</InputLabel>
              <Select
                labelId="source-label"
                value={source}
                label="Source"
                onChange={(e) => setSource(e.target.value as 'moxfield' | 'archidekt')}
              >
                <MenuItem value="moxfield">Moxfield</MenuItem>
                <MenuItem value="archidekt">Archidekt</MenuItem>
              </Select>
            </FormControl>

            <TextField
              type="url"
              value={deckUrl}
              onChange={(e) => setDeckUrl(e.target.value)}
              placeholder="https://moxfield.com/decks..."
              required
              label="URL"
              sx={{ flex: 1, minWidth: 240 }}
            />

            <Button type="submit" variant="contained" disabled={creating} sx={{ whiteSpace: 'nowrap' }}>
              {creating ? 'Creating…' : 'Submit'}
            </Button>
          </Box>
        </Box>

        {createMessage && <Typography sx={{ mt: 2 }}>{createMessage}</Typography>}
      </Box>
    </Container>
  )
}
