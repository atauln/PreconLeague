import { useEffect, useMemo, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Button,
  Paper,
  Checkbox,
  FormControlLabel,
} from '@mui/material'

interface Deck {
  deck_id: number
  deck_name: string
}

interface SnapshotPoint {
  snapshot_id: number
  created_at?: string | null
  week_of_league?: number | null
  overall_rating?: number | null
  bracket_rating?: number | null
  salt_rating?: number | null
  price_usd?: number | null
}

const remoteApi = (import.meta.env.VITE_API_URL as string) || ''
const apiUrl = (path: string) => (remoteApi ? `${remoteApi}/api${path}` : `/api${path}`)

function formatNumber(n?: number | null) {
  if (n === null || n === undefined) return '—'
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(n)
}

// Very small SVG line chart (no deps). Expects points sorted by x ascending.
function LineChart({
  data,
  width = 700,
  height = 200,
  stroke = '#1976d2',
}: {
  data: { x: string; y: number | null }[]
  width?: number
  height?: number
  stroke?: string
}) {
  if (!data || data.length === 0) return <Box sx={{ p: 2 }}>No data</Box>

  const ys = data.map((d) => (d.y === null || d.y === undefined ? NaN : d.y))
  const yNumbers = ys.filter((v) => Number.isFinite(v)) as number[]
  const minY = yNumbers.length ? Math.min(...yNumbers) : 0
  const maxY = yNumbers.length ? Math.max(...yNumbers) : 1
  const pad = (maxY - minY) * 0.1 || 1
  const y0 = minY - pad
  const y1 = maxY + pad

  // leave space on left for y-axis labels
  const leftMargin = 56
  const rightMargin = 12
  const chartWidth = Math.max(50, width - leftMargin - rightMargin)
  const chartHeight = height

  const px = (i: number) => (data.length === 1 ? leftMargin + chartWidth / 2 : leftMargin + (i / (data.length - 1)) * chartWidth)
  const py = (v: number) => ((1 - (v - y0) / (y1 - y0)) * chartHeight)

  const path = data
    .map((pt, i) => {
      const v = Number(pt.y)
      if (!Number.isFinite(v)) return null
      const x = px(i)
      const y = py(v)
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .filter(Boolean)
    .join(' ')

  // Y axis ticks (5 ticks)
  const ticks = 5
  const tickValues = Array.from({ length: ticks }, (_, i) => y0 + ((y1 - y0) * (ticks - 1 - i)) / (ticks - 1))

  return (
    <Box sx={{ overflow: 'auto', p: 2 }}>
      <svg width={width} height={height} role="img" aria-label="line chart">
        <rect x={0} y={0} width={width} height={height} fill="#fff" />
        {/* grid lines + y labels */}
        {tickValues.map((tv, idx) => {
          const t = idx / (ticks - 1)
          const y = t * chartHeight
          return (
            <g key={idx}>
              <line x1={leftMargin} x2={leftMargin + chartWidth} y1={y} y2={y} stroke="#eee" />
              <text x={leftMargin - 8} y={y + 4} textAnchor="end" fontSize={12} fill="#666">{new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(tv)}</text>
            </g>
          )
        })}
        {/* path */}
        {path && <path d={path} fill="none" stroke={stroke} strokeWidth={2} />}
        {/* points */}
        {data.map((pt, i) => {
          const v = Number(pt.y)
          if (!Number.isFinite(v)) return null
          const x = px(i)
          const y = py(v)
          return <circle key={i} cx={x} cy={y} r={3} fill={stroke} />
        })}
      </svg>
      <Box sx={{ display: 'flex', gap: 2, mt: 1, flexWrap: 'wrap' }}>
        {data.map((d) => (
          <Typography key={d.x} variant="caption">{d.x}</Typography>
        ))}
      </Box>
    </Box>
  )
}

export default function Analytics() {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loadingDecks, setLoadingDecks] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null)
  const [snapshots, setSnapshots] = useState<SnapshotPoint[]>([])
  const [loadingSnapshots, setLoadingSnapshots] = useState(false)

  const [showOverall, setShowOverall] = useState(true)
  const [showBracket, setShowBracket] = useState(true)
  const [showSalt, setShowSalt] = useState(true)

  useEffect(() => {
    void loadDecks()
  }, [])

  async function loadDecks() {
    setLoadingDecks(true)
    try {
      const res = await fetch(apiUrl('/decks/'))
      if (!res.ok) throw new Error(`Decks fetch failed: ${res.status}`)
      const json = await res.json()
      const list = Array.isArray(json) ? json : []
  const mapped = list.map((d: { deck_id: number; deck_name: string }) => ({ deck_id: d.deck_id, deck_name: d.deck_name })) as Deck[]
      setDecks(mapped)
      if (mapped.length > 0) setSelectedDeckId(mapped[0].deck_id)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoadingDecks(false)
    }
  }

  useEffect(() => {
    if (selectedDeckId === null) return
    void loadSnapshotsForDeck(selectedDeckId)
  }, [selectedDeckId])

  async function loadSnapshotsForDeck(deckId: number) {
    setLoadingSnapshots(true)
    setError(null)
    try {
      const res = await fetch(apiUrl(`/snapshots/deck/${deckId}`))
      if (!res.ok) throw new Error(`Snapshots fetch failed: ${res.status}`)
      const json = await res.json()
      const snaps = Array.isArray(json) ? json : []
      // map to necessary fields and sort by created_at asc
      const mapped = snaps
        .map((s: { snapshot_id: number; created_at?: string | null; week_of_league?: number | null; overall_rating?: number | null; bracket_rating?: number | null; salt_rating?: number | null; price_usd?: number | null }) => ({
          snapshot_id: s.snapshot_id,
          created_at: s.created_at,
          week_of_league: s.week_of_league,
          overall_rating: s.overall_rating,
          bracket_rating: s.bracket_rating,
          salt_rating: s.salt_rating,
          price_usd: s.price_usd,
        }))
        .sort((a: SnapshotPoint, b: SnapshotPoint) => {
          const ta = a.created_at ? new Date(a.created_at).getTime() : 0
          const tb = b.created_at ? new Date(b.created_at).getTime() : 0
          return ta - tb
        })
      setSnapshots(mapped)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoadingSnapshots(false)
    }
  }

  const overallSeries = useMemo(() => snapshots.map((s) => ({ x: s.week_of_league ? `W${s.week_of_league}` : (s.created_at ?? '—'), y: s.overall_rating ?? null })), [snapshots])
  const bracketSeries = useMemo(() => snapshots.map((s) => ({ x: s.week_of_league ? `W${s.week_of_league}` : (s.created_at ?? '—'), y: s.bracket_rating ?? null })), [snapshots])
  const saltSeries = useMemo(() => snapshots.map((s) => ({ x: s.week_of_league ? `W${s.week_of_league}` : (s.created_at ?? '—'), y: s.salt_rating ?? null })), [snapshots])

  return (
    <Container sx={{ py: 4 }} maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Analytics</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button component={RouterLink} to="/" variant="outlined">Home</Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box mb={2} display="flex" gap={2} alignItems="center">
        <FormControl size="small" sx={{ minWidth: 320 }}>
          <InputLabel id="deck-select-label">Deck</InputLabel>
          <Select
            labelId="deck-select-label"
            label="Deck"
            value={selectedDeckId ?? ''}
            onChange={(e) => setSelectedDeckId(Number(e.target.value))}
          >
            {loadingDecks && <MenuItem value="">Loading…</MenuItem>}
            {!loadingDecks && decks.map((d) => (
              <MenuItem key={d.deck_id} value={d.deck_id}>{d.deck_name}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControlLabel control={<Checkbox checked={showOverall} onChange={(e) => setShowOverall(e.target.checked)} />} label="Overall" />
        <FormControlLabel control={<Checkbox checked={showBracket} onChange={(e) => setShowBracket(e.target.checked)} />} label="Bracket" />
        <FormControlLabel control={<Checkbox checked={showSalt} onChange={(e) => setShowSalt(e.target.checked)} />} label="Salt" />
      </Box>

      {loadingSnapshots ? (
        <Box display="flex" justifyContent="center" my={4}><CircularProgress /></Box>
      ) : (
        <>
          <Paper sx={{ mb: 2 }}>
            <Box sx={{ p: 2 }}>
              <Typography variant="h6">Trend charts</Typography>
              <Typography variant="body2" color="text.secondary">Shows historical snapshot metrics for the selected deck.</Typography>
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2, p: 2 }}>
              {showOverall && (
                <Box>
                  <Typography variant="subtitle2">Overall Rating</Typography>
                  <LineChart data={overallSeries} />
                </Box>
              )}
              {showBracket && (
                <Box>
                  <Typography variant="subtitle2">Bracket Rating</Typography>
                  <LineChart data={bracketSeries} stroke="#9c27b0" />
                </Box>
              )}
              {showSalt && (
                <Box>
                  <Typography variant="subtitle2">Salt Rating</Typography>
                  <LineChart data={saltSeries} stroke="#ff5722" />
                </Box>
              )}
            </Box>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Latest snapshot</Typography>
            {snapshots.length === 0 ? (
              <Typography color="text.secondary" sx={{ mt: 1 }}>No snapshots available for this deck.</Typography>
            ) : (
              <Box sx={{ mt: 1 }}>
                <Typography>Most recent: {snapshots[snapshots.length - 1].created_at ?? '—'}</Typography>
                <Box sx={{ display: 'flex', gap: 4, mt: 1 }}>
                  <Typography>Overall: {formatNumber(snapshots[snapshots.length - 1].overall_rating)}</Typography>
                  <Typography>Bracket: {formatNumber(snapshots[snapshots.length - 1].bracket_rating)}</Typography>
                  <Typography>Salt: {formatNumber(snapshots[snapshots.length - 1].salt_rating)}</Typography>
                  <Typography>Price: {snapshots[snapshots.length - 1].price_usd ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(snapshots[snapshots.length - 1].price_usd as number) : '—'}</Typography>
                </Box>
              </Box>
            )}
          </Paper>
        </>
      )}
    </Container>
  )
}
