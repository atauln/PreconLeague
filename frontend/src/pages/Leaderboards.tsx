import { useEffect, useMemo, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Paper,
  Link as MuiLink,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'

interface SnapshotWithDeck {
  snapshot_id: number
  deck_id: number
  deck_name?: string
  user_id?: number
  user_name?: string
  commander_id?: string | null
  created_at?: string | null
  week_of_league?: number | null
  bracket_rating?: number | null
  salt_rating?: number | null
  price_usd?: number | null
  threat_rating?: number | null
  overall_rating?: number | null
  power_level_rating?: number | null
  synergy_rating?: number | null
  combo_rating?: number | null
  manabase_score?: number | null
  mana_fixing_score?: number | null
  competitive_intent?: number | null
  commander_tier?: number | null
  card_quality?: number | null
}

const remoteApi = (import.meta.env.VITE_API_URL as string) || ''
const apiUrl = (path: string) => (remoteApi ? `${remoteApi}/api${path}` : `/api${path}`)

const METRICS: { key: keyof SnapshotWithDeck; label: string }[] = [
  { key: 'bracket_rating', label: 'Bracket Rating' },
  { key: 'salt_rating', label: 'Salt Rating' },
  { key: 'price_usd', label: 'Price (USD)' },
  { key: 'overall_rating', label: 'Overall Rating' },
  { key: 'power_level_rating', label: 'Power Level' },
  { key: 'synergy_rating', label: 'Synergy' },
  { key: 'manabase_score', label: 'Manabase Score' },
  { key: 'card_quality', label: 'Card Quality' },
]

export default function Leaderboards() {
  const [allSnapshots, setAllSnapshots] = useState<SnapshotWithDeck[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [selectedWeek, setSelectedWeek] = useState<number | 'latest' | null>(null)
  const [selectedMetric, setSelectedMetric] = useState<keyof SnapshotWithDeck>('bracket_rating')

  useEffect(() => {
    void loadAllSnapshots()
  }, [])

  async function loadAllSnapshots() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(apiUrl('/snapshots/'))
      if (!res.ok) throw new Error(`Failed to fetch snapshots: ${res.status}`)
      const json = (await res.json()) as SnapshotWithDeck[]
      // json from API includes deck_name and user_name (see db.get_all_snapshots)
      const snapshots = Array.isArray(json) ? json : []
      setAllSnapshots(snapshots)
      // pick latest week by default (only numeric weeks)
      const weeks = Array.from(
        new Set(snapshots.map((s) => s.week_of_league).filter((w): w is number => typeof w === 'number')),
      )
      if (weeks.length > 0) {
        const maxWeek = Math.max(...weeks)
        setSelectedWeek(maxWeek)
      } else {
        setSelectedWeek(null)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  const availableWeeks = useMemo(() => {
    const w = Array.from(new Set(allSnapshots.map((s) => s.week_of_league).filter((n) => n !== undefined && n !== null))) as number[]
    return w.sort((a, b) => b - a)
  }, [allSnapshots])

  // Build leaderboard entries based on selected week and metric
  const leaderboard = useMemo(() => {
    if (!allSnapshots || allSnapshots.length === 0 || selectedWeek === null) return [] as SnapshotWithDeck[]

    // Filter snapshots for week
    const snapsForWeek = allSnapshots.filter((s) => s.week_of_league === selectedWeek)

    // For each deck_id pick the most recent snapshot (by created_at)
    const byDeck: Record<number, SnapshotWithDeck> = {}
    snapsForWeek.forEach((s) => {
      const existing = byDeck[s.deck_id]
      if (!existing) byDeck[s.deck_id] = s
      else {
        const a = new Date(existing.created_at || '')
        const b = new Date(s.created_at || '')
        if (Number.isNaN(a.getTime()) || b.getTime() > a.getTime()) {
          byDeck[s.deck_id] = s
        }
      }
    })

    const rows = Object.values(byDeck)
    // sort by selected metric descending; handle nulls
    rows.sort((x, y) => {
      const xv = (x[selectedMetric] as number) ?? -Infinity
      const yv = (y[selectedMetric] as number) ?? -Infinity
      // ensure numbers; price_usd may be float
      return Number(yv) - Number(xv)
    })

    return rows
  }, [allSnapshots, selectedWeek, selectedMetric])

  function formatValue(val: unknown, key: keyof SnapshotWithDeck) {
    if (val === null || val === undefined) return '—'
    if (key === 'price_usd') return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(val as number))
    const n = Number(String(val))
    return Number.isFinite(n) ? new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(n) : String(val)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Typography variant="h5">Leaderboards</Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button component={RouterLink} to="/" variant="outlined" size="small" sx={{ minHeight: '44px' }}>Home</Button>
          <Button onClick={() => void loadAllSnapshots()} variant="contained" size="small" sx={{ minHeight: '44px' }}>Refresh</Button>
        </Box>
      </Box>

      <Box mb={2} display="flex" gap={2} alignItems="center" flexWrap="wrap">
        <FormControl sx={{ minWidth: { xs: '100%', sm: 180 } }} size="small">
          <InputLabel id="week-label">Week</InputLabel>
          <Select
            labelId="week-label"
            label="Week"
            value={selectedWeek === null ? 'none' : selectedWeek}
            onChange={(e) => {
              const v = e.target.value
              if (v === 'none') setSelectedWeek(null)
              else setSelectedWeek(Number(v))
            }}
            sx={{ minHeight: '44px' }}
          >
            {availableWeeks.length === 0 && <MenuItem value="none">No weeks available</MenuItem>}
            {availableWeeks.map((wk) => (
              <MenuItem key={wk} value={wk}>{`Week ${wk}`}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: { xs: '100%', sm: 220 } }} size="small">
          <InputLabel id="metric-label">Metric</InputLabel>
          <Select
            labelId="metric-label"
            label="Metric"
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value as keyof SnapshotWithDeck)}
            sx={{ minHeight: '44px' }}
          >
            {METRICS.map((m) => (
              <MenuItem key={String(m.key)} value={m.key}>{m.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {loading && <Box my={2}><CircularProgress /></Box>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {!loading && !error && (
        <Box sx={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
          <Paper sx={{ width: 'max-content' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>#</TableCell>
                  <TableCell>Deck</TableCell>
                  <TableCell>Owner</TableCell>
                  <TableCell align="right">{METRICS.find(m => m.key === selectedMetric)?.label}</TableCell>
                  <TableCell align="right">Overall</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaderboard.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5}><Typography sx={{ p: 2 }}>No data for the selected week.</Typography></TableCell>
                  </TableRow>
                )}
                {leaderboard.map((row, idx) => (
                  <TableRow key={row.snapshot_id}>
                    <TableCell>{idx + 1}</TableCell>
                    <TableCell sx={{ minWidth: '150px' }}>
                      {row.deck_id ? (
                        <MuiLink component={RouterLink} to={`/decks/${row.deck_id}`} underline="hover" sx={{ wordBreak: 'break-word' }}>
                          {row.deck_name ?? `Deck ${row.deck_id}`}
                        </MuiLink>
                      ) : (
                        row.deck_name ?? `Deck ${row.deck_id}`
                      )}
                    </TableCell>
                    <TableCell>{row.user_name ?? row.user_id ?? '—'}</TableCell>
                    <TableCell align="right">{formatValue(row[selectedMetric], selectedMetric)}</TableCell>
                    <TableCell align="right">{formatValue(row.overall_rating, 'overall_rating')}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Box>
      )}
    </Container>
  )
}
