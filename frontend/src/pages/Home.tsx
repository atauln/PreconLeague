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
  Avatar,
  CardMedia,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material'
import InfoOutlined from '@mui/icons-material/InfoOutlined'

interface Snapshot {
  snapshot_id: number
  deck_id: number
  commander_id: string | null
  created_at: string
  salt_rating: number
  synergy_rating: number
  power_level_rating: number
  threat_rating: number
  bracket_rating: number
  overall_rating: number
  manabase_score: number
  power_level_display_value: number
  combo_rating: number
  archetype_minor: string | null
  archetype_major: string | null
  price_usd: number | null
  week_of_league: number | null
}

interface Deck {
  deck_id: number
  user_id: number
  user_name?: string
  moxfield_deck_url?: string | null
  archidekt_deck_url?: string | null
  source: string
  deck_name: string
  most_recent_snapshot: Snapshot | null
  colors: string[]
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

const START_DATE_OF_LEAGUE = new Date('2026-01-12T00:00:00Z')
const CURRENT_WEEK_OF_LEAGUE = Math.floor((Date.now() - START_DATE_OF_LEAGUE.getTime()) / (7 * 24 * 60 * 60 * 1000)) + 1

export default function Home() {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [source, setSource] = useState<'moxfield' | 'archidekt'>('moxfield')
  const [deckUrl, setDeckUrl] = useState('')
  const [creating, setCreating] = useState(false)
  const [createMessage, setCreateMessage] = useState<string | null>(null)
  const [rulesOpen, setRulesOpen] = useState(false)

  const openRules = () => setRulesOpen(true)
  const closeRules = () => setRulesOpen(false)

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
      if (!Array.isArray(data)) {
        setDecks([])
        return
      }

      // Fetch each deck's most recent snapshot (and commander card data) in parallel.
      // We catch errors per-deck so a failure for one deck doesn't abort the whole batch.
      const deckPromises = data.map(async (deck: any) => {
        try {
          const snapshot = await fetchMostRecentSnapshot(deck.deck_id)
          deck.most_recent_snapshot = snapshot
          if (snapshot && snapshot.commander_id) {
            try {
              const cardData = await fetchCardData(snapshot.commander_id)
              deck.colors = cardData.color_identity || []
            } catch (cardErr) {
              console.warn(`Failed to fetch card data for commander ${snapshot.commander_id}:`, cardErr)
              deck.colors = []
            }
          } else {
            deck.colors = []
          }
        } catch (err) {
          console.warn(`Failed to fetch most recent snapshot for deck ${deck.deck_id}:`, err)
          deck.most_recent_snapshot = null
          deck.colors = []
        }
        return deck
      })

      const enriched = await Promise.all(deckPromises)
      setDecks(enriched)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  async function fetchCardData(cardId: string) {
    const res = await fetch('https://api.scryfall.com/cards/' + cardId)
    if (!res.ok) {
      throw new Error(`Failed to fetch card data: ${res.status} ${res.statusText}`)
    }
    const data = await res.json()
    return data
  }

  async function fetchMostRecentSnapshot(deckId: number) {
    const res = await fetch(apiUrl(`/decks/most_recent_snapshot/${deckId}`))
    if (!res.ok) {
      throw new Error(`Failed to fetch most recent snapshot: ${res.status} ${res.statusText}`)
    }
    const data = await res.json()
    return data
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

      // Create an initial snapshot for the newly-registered deck before returning
      try {
        const snapRes = await fetch(apiUrl(`/snapshots/create_snapshot/${data.deck_id}`), { method: 'POST' })
        if (!snapRes.ok) {
          const snapText = await snapRes.text().catch(() => '')
          console.warn(`Initial snapshot failed for deck ${data.deck_id}:`, snapRes.status, snapText)
          setCreateMessage((prev) => `${prev} — snapshot creation failed (${snapRes.status})`)
        } else {
          setCreateMessage((prev) => `${prev} — initial snapshot created`)
        }
      } catch (snapErr: unknown) {
        console.warn('Initial snapshot error:', snapErr)
        setCreateMessage((prev) => `${prev} — snapshot error: ${snapErr instanceof Error ? snapErr.message : String(snapErr)}`)
      }

      // Refresh list after attempting snapshot creation
      await fetchDecks()
    } catch (err: unknown) {
      setCreateMessage(`Error: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setCreating(false)
    }
  }


  return (
    <>
    <Container maxWidth={false} sx={{ py: 4, px: 2 }}>
      <Box mb={3}>
        <Typography variant="h5">Precon League — Home</Typography>
        <Typography color="text.secondary">Choose a deck to edit (this demo is unauthenticated — any user can open any deck).</Typography>
      </Box>

      <Box mb={4} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">All decks</Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button component={RouterLink} to="/leaderboards" variant="contained">Leaderboards</Button>
          <Button component={RouterLink} to="/analytics" variant="outlined">Analytics</Button>
          <Tooltip title="Sample rules for the week">
            <IconButton onClick={openRules} aria-label="weekly rules">
              <InfoOutlined />
            </IconButton>
          </Tooltip>
        </Box>
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
                  <Box sx={{ minWidth: 25}}>
                    {d.colors.map((color) => (
                      <Avatar
                        key={color}
                        src={`https://svgs.scryfall.io/card-symbols/${color}.svg`}
                        alt={`${color} mana`}
                        variant="square"
                        sx={{ width: 20, height: 20, bgcolor: 'transparent' }}
                      />
                    ))}
                  </Box>
                  {d.most_recent_snapshot !== null && d.most_recent_snapshot.commander_id && (
                    <MuiLink
                      component={RouterLink}
                      to={`/decks/${d.deck_id}`}
                      sx={{ display: 'block', textDecoration: 'none' }}
                    >
                      <CardMedia
                        component="img"
                        image={`https://cards.scryfall.io/art_crop/front/${d.most_recent_snapshot.commander_id.charAt(0)}/${d.most_recent_snapshot.commander_id.charAt(1)}/${d.most_recent_snapshot.commander_id}.jpg`}
                        alt={`${d.deck_name} commander art`}
                        sx={{ height: 100, width: 'auto', objectFit: 'cover', borderRadius: 1 }}
                        loading="lazy"
                        onError={(e: any) => { e.currentTarget.onerror = null; e.currentTarget.src = '/fallback.jpg' }}
                      />
                    </MuiLink>
                  )}
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
      <Dialog open={rulesOpen} onClose={closeRules} fullWidth maxWidth="sm">
        <DialogTitle>Rules for Week {CURRENT_WEEK_OF_LEAGUE}</DialogTitle>
        <DialogContent dividers>
          <Typography sx={{ mb: 1 }}>
            These are the rules for the current week of the Precon League:
          </Typography>
            <Typography sx={{ mb: 2 }}>
              Bombs rotate weekly. This week's bomb is a 
              <Typography component="span" sx={{ fontWeight: 'bold', color: 'primary.main', mx: 0.5 }}>
              {CURRENT_WEEK_OF_LEAGUE % 2 === 1 ? 'land' : 'nonland'}
              </Typography>
              card.
            </Typography>
            <ul>
            <li style={{ marginBottom: '8px' }}>Each week you may swap in up to 5 land cards (each under $5), and up to 5 nonland cards (each under $5).</li>
            <li style={{ marginBottom: '8px' }}>In addition, depending on the week, you may swap in one "bomb" card (land or nonland) under $25.</li>
            <li style={{ marginBottom: '8px' }}>You may swap out any cards from your deck, but must adhere to the above limits for cards swapped in.</li>
            <li style={{ marginBottom: '8px' }}>Card pricing is determined by the lowest available price from either:
              <ul>
              <li style={{ marginBottom: '4px' }}>Millennium (any condition)</li>
              <li>TCGPlayer/online vendor</li>
              </ul>
            </li>
            <li style={{ marginBottom: '8px' }}>You may use special printings of cards (e.g., Secret Lair, special guests) even if they exceed the pricing criteria above.
              <ul>
              <li style={{ marginBottom: '4px' }}>For example, if a regular printing of a card is $6 but a special printing is $4, you may use the special printing.</li>
              <li>Alternatively, if the special printing is $6 but there is an available regular printing under $5, you may still use the special printing.</li>
              </ul>
            </li>
            <li style={{ marginBottom: '8px' }}>There are currently no restrictions on card art choices.</li>
            </ul>
        </DialogContent>
        <DialogActions>
        </DialogActions>
      </Dialog>
    </>
  )
}
