import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, Link as RouterLink } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Table,
  TableBody,
  TableRow,
  TableCell,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
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
  commander_id: string
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
  const [selectedSnapshot, setSelectedSnapshot] = useState<Snapshot | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [cardNames, setCardNames] = useState<Record<string, string>>({})
  const cardFetchInFlight = useRef<Set<string>>(new Set())
  const [weekEdits, setWeekEdits] = useState<Record<number, number>>({})
  const [updatingWeek, setUpdatingWeek] = useState<Record<number, boolean>>({})
  const [modalEditingWeek, setModalEditingWeek] = useState(false)

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

  function fetchCardName(cardId: string): string {
    if (!cardId) return ''
    const cached = cardNames[cardId]
    if (cached) return cached

    // If already fetching this id, return fallback and wait for update
    if (!cardFetchInFlight.current.has(cardId)) {
      cardFetchInFlight.current.add(cardId)
      fetch(`https://api.scryfall.com/cards/${cardId}`)
        .then((res) => {
          if (!res.ok) throw new Error(`Card fetch failed: ${res.status}`)
          return res.json()
        })
        .then((data) => {
          const name = (data && data.name) ? data.name : cardId
          setCardNames((prev) => ({ ...prev, [cardId]: name }))
        })
        .catch(() => {
          // Cache fallback to avoid repeated failing requests
          setCardNames((prev) => ({ ...prev, [cardId]: cardId }))
        })
        .finally(() => {
          cardFetchInFlight.current.delete(cardId)
        })
    }

    return cardId
  }

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

  function openDetails(s: Snapshot) {
    setSelectedSnapshot(s)
    setWeekEdits((prev) => ({ ...prev, [s.snapshot_id]: s.week_of_league }))
    setModalEditingWeek(false)
    setModalOpen(true)
  }

  function closeDetails() {
    setModalOpen(false)
    setSelectedSnapshot(null)
  }

  async function handleUpdateWeek(snapshotId: number) {
    const newWeek = weekEdits[snapshotId]
    if (newWeek === undefined || newWeek === null || Number.isNaN(newWeek) || newWeek < 0) {
      setError('Please enter a valid week number')
      return
    }
    setUpdatingWeek((prev) => ({ ...prev, [snapshotId]: true }))
    setError(null)
    try {
      const res = await fetch(apiUrl(`/snapshots/${snapshotId}/week/${newWeek}`), { method: 'PUT' })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Update week failed: ${res.status} ${text}`)
      }
      await fetchData()
      // Refresh the selected snapshot with latest data from the API
      try {
        const single = await fetch(apiUrl(`/snapshots/${snapshotId}`))
        if (single.ok) {
          const updated = await single.json()
          setSelectedSnapshot(updated)
        }
      } catch (_) {
        // ignore
      }
      setModalEditingWeek(false)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setUpdatingWeek((prev) => ({ ...prev, [snapshotId]: false }))
    }
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
            {snapshots.length > 0 && snapshots[0]?.commander_id && (
              <Typography variant="body1">{fetchCardName(snapshots[0].commander_id)}</Typography>
            )}
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
          <Grid key={s.snapshot_id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Typography variant="subtitle1">{s.snapshot_name || `Snapshot ${s.snapshot_id}`}</Typography>
                  <Typography color="text.secondary">{formatDate(s.created_at)}</Typography>
                </Box>

                <Box display="flex" alignItems="center" justifyContent="space-between" mt={1}>
                  <Box style={{ paddingRight: '1rem' }}>
                    <Typography variant="body2">Commander: {fetchCardName(s.commander_id)}</Typography>
                    <Typography variant="body2">Power Level: {formatNumber(s.power_level_rating, 3)}</Typography>
                  </Box>
                  <Box>
                    <Button variant="outlined" size="small" onClick={() => openDetails(s)} sx={{ mr: 1 }}>Details</Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={modalOpen} onClose={closeDetails} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedSnapshot ? selectedSnapshot.snapshot_name || `Snapshot ${selectedSnapshot.snapshot_id}` : 'Snapshot Details'}</DialogTitle>
        <DialogContent dividers>
          {selectedSnapshot && (
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>Commander</TableCell>
                  <TableCell>{fetchCardName(selectedSnapshot.commander_id)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Overall Rating</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.overall_rating, 1)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Power Level</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.power_level_rating, 2)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Salt Rating</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.salt_rating, 1)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Synergy</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.synergy_rating, 1)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Threat</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.threat_rating, 1)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Bracket</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.bracket_rating, 2)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Combo</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.combo_rating, 1)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Manabase Score</TableCell>
                  <TableCell>{formatNumber(selectedSnapshot.manabase_score, 0)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Archetype</TableCell>
                  <TableCell>{selectedSnapshot.archetype_major} - {selectedSnapshot.archetype_minor}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Price</TableCell>
                  <TableCell>{formatCurrency(selectedSnapshot.price_usd)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Week</TableCell>
                  <TableCell>
                    {!modalEditingWeek ? (
                      <Box display="flex" alignItems="center">
                        <Typography sx={{ mr: 1 }}>{selectedSnapshot.week_of_league}</Typography>
                        <Button size="small" onClick={() => setModalEditingWeek(true)}>EDIT</Button>
                      </Box>
                    ) : (
                      <Box display="flex" alignItems="center">
                        <TextField
                          type="number"
                          size="small"
                          inputProps={{ min: 0 }}
                          sx={{ width: 100, mr: 1 }}
                          value={weekEdits[selectedSnapshot.snapshot_id] ?? selectedSnapshot.week_of_league}
                          onChange={(e) => setWeekEdits((prev) => ({ ...prev, [selectedSnapshot.snapshot_id]: Number(e.target.value) }))}
                        />
                        <Button
                          size="small"
                          onClick={() => void handleUpdateWeek(selectedSnapshot.snapshot_id)}
                          disabled={!!updatingWeek[selectedSnapshot.snapshot_id]}
                        >
                          {updatingWeek[selectedSnapshot.snapshot_id] ? 'Updating…' : 'Update'}
                        </Button>
                        <Button
                          size="small"
                          onClick={() => {
                            setModalEditingWeek(false)
                            setWeekEdits((prev) => ({ ...prev, [selectedSnapshot.snapshot_id]: selectedSnapshot.week_of_league }))
                          }}
                          sx={{ ml: 1 }}
                        >
                          Cancel
                        </Button>
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
