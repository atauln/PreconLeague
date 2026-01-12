import { useEffect, useState, useCallback } from 'react'
import { useParams, Link as RouterLink } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableRow,
  TableCell,
  CircularProgress,
  Alert,
  Link as MuiLink,
} from '@mui/material'

interface Deck {
  deck_id: number
  user_id: number
  moxfield_deck_url?: string | null
  archidekt_deck_url?: string | null
  source: string
  deck_name: string
}

interface Snapshot {
  snapshot_id: number
  deck_id: number
  snapshot_name?: string | null
  created_at?: string
  commander_id: number
  overall_rating: number
  power_level_rating: number
  salt_rating: number
  synergy_rating: number
  threat_rating: number
  bracket_rating: number
  combo_rating: number
  manabase_score: number
  archetype_minor: string
  archetype_major: string
  price_usd: number
  week_of_league: number
}

const remoteApi = (import.meta.env.VITE_API_URL as string) || ''
const apiUrl = (path: string) => (remoteApi ? `${remoteApi}${path}` : `/api${path}`)

export default function DeckEditor() {
  const { deckId } = useParams<{ deckId: string }>()
  const id = Number(deckId)
  const [deck, setDeck] = useState<Deck | null>(null)
  const [snapshots, setSnapshots] = useState<Snapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const fetchData = useCallback(async function () {
    if (isNaN(id)) return
    setLoading(true)
    setError(null)
    try {
      const [deckRes, snapsRes] = await Promise.all([
        fetch(apiUrl(`/decks/${id}`)),
        fetch(apiUrl(`/snapshots/deck/${id}`)),
      ])
      if (!deckRes.ok) throw new Error(`Deck fetch failed: ${deckRes.status}`)
      if (!snapsRes.ok && snapsRes.status !== 404) throw new Error(`Snapshots fetch failed: ${snapsRes.status}`)
      const deckData = await deckRes.json()
      const snapsData = snapsRes.ok ? await snapsRes.json() : []
      setDeck(deckData)
      setSnapshots(snapsData || [])
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    void fetchData()
  }, [fetchData])

  async function handleCreateSnapshot() {
    if (isNaN(id)) return
    setCreating(true)
    try {
      const res = await fetch(apiUrl(`/snapshots/create_snapshot/${id}`), { method: 'POST' })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Create snapshot failed: ${res.status} ${text}`)
      }
      await fetchData()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setCreating(false)
    }
  }

  function formatNumber(value?: number | null, maximumFractionDigits = 1) {
    if (value === null || value === undefined || Number.isNaN(value as number)) return '—'
    return new Intl.NumberFormat('en-US', { maximumFractionDigits, minimumFractionDigits: 0 }).format(value as number)
  }

  function formatCurrency(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value as number)) return '—'
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value as number)
  }

  function formatDate(iso?: string | null) {
    if (!iso) return '—'
    const d = new Date(iso)
    if (Number.isNaN(d.getTime())) return iso
    return d.toLocaleString()
  }

  if (!deckId || isNaN(id)) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography variant="body1">Invalid deck id. <MuiLink component={RouterLink} to="/">Back</MuiLink></Typography>
      </Container>
    )
  }

  return (
    <Container sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Deck editor</Typography>
        <MuiLink component={RouterLink} to="/">← Back to home</MuiLink>
      </Box>

      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {deck && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6">{deck.deck_name}</Typography>
            <Typography color="text.secondary">Owner id: {deck.user_id}</Typography>
            <Typography color="text.secondary">Source: {deck.source}</Typography>
            <Box mt={1}>
              {deck.moxfield_deck_url && (
                <MuiLink href={deck.moxfield_deck_url} target="_blank" rel="noreferrer" sx={{ mr: 2 }}>View Moxfield</MuiLink>
              )}
              {deck.archidekt_deck_url && (
                <MuiLink href={deck.archidekt_deck_url} target="_blank" rel="noreferrer">View Archidekt</MuiLink>
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      <Box mb={2} display="flex" alignItems="center" justifyContent="space-between">
        <Typography variant="h6">Snapshots</Typography>
        <Button variant="contained" onClick={handleCreateSnapshot} disabled={creating || loading}>
          {creating ? 'Creating snapshot…' : 'Create snapshot from source'}
        </Button>
      </Box>

      {snapshots.length === 0 && !loading && <Typography>No snapshots yet.</Typography>}

      <Grid container spacing={2}>
        {snapshots.map((s) => (
          <Grid key={s.snapshot_id} item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Typography variant="subtitle1">{s.snapshot_name || `Snapshot ${s.snapshot_id}`}</Typography>
                  <Typography color="text.secondary">{formatDate(s.created_at)}</Typography>
                </Box>

                <Table size="small" sx={{ mt: 1 }}>
                  <TableBody>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>Commander ID</TableCell>
                      <TableCell>{s.commander_id}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Overall Rating</TableCell>
                      <TableCell>{formatNumber(s.overall_rating, 1)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Power Level</TableCell>
                      <TableCell>{formatNumber(s.power_level_rating, 2)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Salt Rating</TableCell>
                      <TableCell>{formatNumber(s.salt_rating, 1)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Synergy</TableCell>
                      <TableCell>{formatNumber(s.synergy_rating, 1)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Threat</TableCell>
                      <TableCell>{formatNumber(s.threat_rating, 1)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Bracket</TableCell>
                      <TableCell>{formatNumber(s.bracket_rating, 2)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Combo</TableCell>
                      <TableCell>{formatNumber(s.combo_rating, 1)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Manabase Score</TableCell>
                      <TableCell>{formatNumber(s.manabase_score, 0)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Archetype</TableCell>
                      <TableCell>{s.archetype_major} - {s.archetype_minor}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Price</TableCell>
                      <TableCell>{formatCurrency(s.price_usd)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Week</TableCell>
                      <TableCell>{s.week_of_league}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}
