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
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Link as MuiLink
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { fetchScryfallCard } from '../utils/scryfall'
import { SnapshotDetailsModal, TempSnapshotModal } from './SnapshotModals'

interface Deck {
  deck_id: number
  user_id: number
  user_name?: string
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
  mana_fixing_score: number
  competitive_intent: number
  commander_tier: number
  card_quality: number
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
  const [tempSnapshot, setTempSnapshot] = useState<Partial<Snapshot & { library_cards?: any[]; commanders?: any[] }> | null>(null)
  const [tempModalOpen, setTempModalOpen] = useState(false)
  const [tempPrevSnapshot, setTempPrevSnapshot] = useState<Partial<Snapshot> | null>(null)
  const [cardCache, setCardCache] = useState<Record<string, any>>({})
  const cardFetchInFlight = useRef<Set<string>>(new Set())
  const [weekEdits, setWeekEdits] = useState<Record<number, number>>({})
  const [updatingWeek, setUpdatingWeek] = useState<Record<number, boolean>>({})
  const [modalEditingWeek, setModalEditingWeek] = useState(false)
  const [compareWeek, setCompareWeek] = useState<number | null>(null)

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

  function fetchCardObject(cardId: string): any | null {
    if (!cardId) return null
    const cached = cardCache[cardId]
    if (cached) return cached

    // If already fetching this id, return fallback and wait for update
    if (!cardFetchInFlight.current.has(cardId)) {
      cardFetchInFlight.current.add(cardId)
      fetchScryfallCard(cardId)
        .then((data) => {
          setCardCache((prev) => ({ ...prev, [cardId]: data }))
        })
        .catch(() => {
          // Cache fallback to avoid repeated failing requests
          setCardCache((prev) => ({ ...prev, [cardId]: { name: cardId } }))
        })
        .finally(() => {
          cardFetchInFlight.current.delete(cardId)
        })
    }

    return null
  }

  function getCardName(cardId?: string | null) {
    if (!cardId) return ''
    const obj = fetchCardObject(cardId)
    return obj?.name ?? cardCache[cardId]?.name ?? cardId
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

  function renderStatWithPrevDiff(
    snap: Snapshot,
    statKey: keyof Snapshot,
    formatter: (v?: number | null) => string,
    options?: { percent?: boolean; maximumFractionDigits?: number; compareWeek?: number | null }
  ) {
    const val = snap[statKey] as unknown as number | null
    const formatted = formatter(val)

    // Determine which week to compare to: either explicit compareWeek or previous week
    const targetWeek =
      options && options.compareWeek !== undefined && options.compareWeek !== null
        ? options.compareWeek
        : snap.week_of_league && snap.week_of_league > 0
        ? snap.week_of_league - 1
        : undefined

    if (targetWeek === undefined || targetWeek === null || targetWeek < 0) return <>{formatted}</>

    const prevWeekSnapshots = snapshots.filter((s) => s.week_of_league === targetWeek)
    if (prevWeekSnapshots.length === 0) return <>{formatted}</>

    const prevSnapshot = prevWeekSnapshots.sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime())[0]
    const prevVal = prevSnapshot[statKey] as unknown as number | null

    if (
      prevVal === null ||
      prevVal === undefined ||
      Number.isNaN(prevVal as number) ||
      val === null ||
      val === undefined ||
      Number.isNaN(val as number)
    )
      return <>{formatted}</>

    const diff = (val as number) - (prevVal as number)
    if (diff === 0) return <>{formatted}</>

    const diffFormatted = formatter(diff)

    let percentStr: string | null = null
    if (options?.percent && prevVal !== 0) {
      const percent = (diff / (prevVal as number)) * 100
      const pctFormatter = new Intl.NumberFormat('en-US', {
        maximumFractionDigits: options?.maximumFractionDigits ?? 1,
        minimumFractionDigits: 0,
      })
      percentStr = `${pctFormatter.format(Math.abs(percent))}%`
    }

    return (
      <>
        {formatted}
        <Typography component="span" sx={{ ml: 1, color: diff > 0 ? 'success.main' : 'error.main', fontSize: '0.875rem' }}>
          ({diff > 0 ? '+' : ''}{diffFormatted}{percentStr ? ` / ${percentStr}` : ''})
        </Typography>
      </>
    )
  }

  type ChangedCard = { card_id?: string | null; card_name?: string | null; quantity: number }

  async function getChangedCards(newSnapId: number, oldSnapId: number): Promise<{ added: ChangedCard[]; removed: ChangedCard[] }> {
    // backend now returns arrays of objects: { card_id, card_name, quantity }
    // but keep backward-compat: if strings are returned, treat them as ids with qty=1
    try {
      const res = await fetch(apiUrl(`/snapshots/${newSnapId}/changes/${oldSnapId}`))
      if (!res.ok) throw new Error(`Fetch changed cards failed: ${res.status}`)
      const data = await res.json()

      const normalize = (arr: any): ChangedCard[] => {
        if (!Array.isArray(arr)) return []
        if (arr.length === 0) return []
        // strings (legacy)
        if (typeof arr[0] === 'string') {
          return arr.map((id: string) => ({ card_id: id, card_name: id, quantity: 1 }))
        }
        // objects shape
        return arr.map((it: any) => ({
          card_id: it.card_id ?? it.id ?? null,
          card_name: it.card_name ?? it.name ?? null,
          quantity: Number.isInteger(it.quantity) ? it.quantity : 1,
        }))
      }

      return {
        added: normalize(data.added_cards),
        removed: normalize(data.removed_cards),
      }
    } catch {
      return { added: [], removed: [] }
    }
  }

  const [changedCards, setChangedCards] = useState<{ added: ChangedCard[]; removed: ChangedCard[] } | null>(null)
  const [changedCardsLoading, setChangedCardsLoading] = useState(false)

  useEffect(() => {
    // load changed cards whenever modal opens, selectedSnapshot changes, or compareWeek changes
    if (!selectedSnapshot) {
      setChangedCards(null)
      return
    }

    const targetWeek = compareWeek !== null && compareWeek !== undefined
      ? compareWeek
      : selectedSnapshot.week_of_league && selectedSnapshot.week_of_league > 0
      ? selectedSnapshot.week_of_league - 1
      : undefined

    if (targetWeek === undefined || targetWeek === null) {
      setChangedCards(null)
      return
    }

    const prevWeekSnapshots = snapshots.filter((s) => s.week_of_league === targetWeek)
    if (prevWeekSnapshots.length === 0) {
      setChangedCards(null)
      return
    }

    const prevSnapshot = prevWeekSnapshots.sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime())[0]
    if (!prevSnapshot) {
      setChangedCards(null)
      return
    }

    let cancelled = false
    ;(async () => {
      setChangedCardsLoading(true)
      try {
        const res = await getChangedCards(selectedSnapshot.snapshot_id, prevSnapshot.snapshot_id)
        if (!cancelled) setChangedCards(res)
      } catch {
        if (!cancelled) setChangedCards({ added: [], removed: [] })
      } finally {
        if (!cancelled) setChangedCardsLoading(false)
      }
    })()

    return () => { cancelled = true }
  }, [selectedSnapshot, compareWeek, snapshots])

  function openDetails(s: Snapshot) {
    setSelectedSnapshot(s)
    setWeekEdits((prev) => ({ ...prev, [s.snapshot_id]: s.week_of_league }))
    setModalEditingWeek(false)
    setCompareWeek(null)
    setModalOpen(true)
  }

  function closeDetails() {
    setModalOpen(false)
    setSelectedSnapshot(null)
  }

  function getQuantityofChangedCards(changes: { added: ChangedCard[]; removed: ChangedCard[] }) {
    const addedQty = changes.added.reduce((sum, c) => sum + (c.quantity || 0), 0)
    const removedQty = changes.removed.reduce((sum, c) => sum + (c.quantity || 0), 0)
    return addedQty - removedQty
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

  async function showTempSnapshotData() {
    // fetch data from /decks/{deckId}/temp_snapshot
    // form: "deck_id": deck_id,
        // "commandersalt_data": commandersalt_data,
        // "library_cards": [ {"id": card.id, "name": card.name, "quantity": card.quantity} for card in proc_deck.library ],
        // "commanders": [ {"id": cmdr.id, "name": cmdr.name} for cmdr in proc_deck.commanders ]
    if (isNaN(id)) return
    setLoading(true)
    setError(null)
    setTempPrevSnapshot(null)
    try {
      const res = await fetch(apiUrl(`/snapshots/deck/${id}/temp_snapshot`))
      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Fetch temp snapshot failed: ${res.status} ${text}`)
      }
      const data = await res.json()
      setTempSnapshot(data)
      setTempModalOpen(true)

      // Also fetch the most recent saved snapshot for the deck to compute metric deltas
      try {
        const prevRes = await fetch(apiUrl(`/decks/most_recent_snapshot/${id}`))
        if (prevRes.ok) {
          const prevData = await prevRes.json()
          setTempPrevSnapshot(prevData)
        } else {
          setTempPrevSnapshot(null)
        }
      } catch (_) {
        setTempPrevSnapshot(null)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  function closeTempModal() {
    setTempModalOpen(false)
    setTempSnapshot(null)
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
      <style>{`
        @keyframes rainbow-rotate { 0% { filter: hue-rotate(0deg); } 100% { filter: hue-rotate(360deg); } }
        .rainbow-border { display: inline-block; padding: 1px; border-radius: 6px; background: linear-gradient(90deg, #ff3cac, #784ba0, #2b86c5, #00c9a7, #ffb347); animation: rainbow-rotate 3s linear infinite; }
        .rainbow-inner { display: inline-block; border-radius: 5px; background: transparent; overflow: hidden; }
      `}</style>
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
              <Typography variant="body1">{getCardName(snapshots[0].commander_id)}</Typography>
            )}
            <Typography color="text.secondary">Owner: {deck.user_name ?? deck.user_id}</Typography>
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
        <Box>
          <Button variant="outlined" onClick={() => showTempSnapshotData()} sx={{ paddingRight: '1rem', marginRight: '1rem' }}>
            Get Temporary Snapshot Data
          </Button>
          <Button variant="contained" onClick={handleCreateSnapshot} disabled={creating || loading}>
            {creating ? 'Creating snapshot…' : 'Create snapshot from source'}
          </Button>
        </Box>
      </Box>

      {snapshots.length === 0 && !loading && <Typography>No snapshots yet.</Typography>}

      <Box>
        {(() => {
          const groups = snapshots.reduce((acc: Record<number, Snapshot[]>, s) => {
            const key = s.week_of_league ?? -1
            if (!acc[key]) acc[key] = []
            acc[key].push(s)
            return acc
          }, {})

          const sortedKeys = Object.keys(groups)
            .map((k) => Number(k))
            .sort((a, b) => b - a)

          return sortedKeys.map((wk) => (
            <Accordion key={wk} sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography sx={{ fontWeight: 'bold' }}>{wk >= 0 ? `Week ${wk}` : 'Unassigned'}</Typography>
                <Typography sx={{ ml: 2, color: 'text.secondary' }}>{groups[wk].length} snapshot(s)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2} sx={{ display: 'flex', flexWrap: 'wrap' }}>
                  {groups[wk].map((s) => (
                    <Grid key={s.snapshot_id} sx={{ boxSizing: 'border-box', width: { xs: '100%', sm: '50%', md: '32%' } }}>
                      <Card sx={{ height: 120 }}>
                        <CardContent sx={{ height: '100%', boxSizing: 'border-box' }}>
                          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                            <Typography variant="subtitle1">{s.snapshot_name || `Snapshot ${s.snapshot_id}`}</Typography>
                            <Typography color="text.secondary">{formatDate(s.created_at)}</Typography>
                          </Box>

                          <Box display="flex" alignItems="center" justifyContent="space-between" mt={1}>
                            <Box style={{ paddingRight: '1rem' }}>
                              <Typography variant="body2">Commander: {getCardName(s.commander_id)}</Typography>
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
              </AccordionDetails>
            </Accordion>
          ))
        })()}
      </Box>

      <SnapshotDetailsModal
        open={modalOpen}
        onClose={closeDetails}
        snapshot={selectedSnapshot}
        snapshots={snapshots}
        cardCache={cardCache}
        fetchCardObject={fetchCardObject}
        getCardName={getCardName}
        renderStatWithPrevDiff={renderStatWithPrevDiff}
        formatNumber={formatNumber}
        formatCurrency={formatCurrency}
        weekEdits={weekEdits}
        setWeekEdits={setWeekEdits}
        modalEditingWeek={modalEditingWeek}
        setModalEditingWeek={setModalEditingWeek}
        handleUpdateWeek={handleUpdateWeek}
        updatingWeek={updatingWeek}
        compareWeek={compareWeek}
        setCompareWeek={setCompareWeek}
        changedCards={changedCards}
        changedCardsLoading={changedCardsLoading}
        getQuantityofChangedCards={getQuantityofChangedCards}
      />
      {/* Temporary snapshot preview dialog (mirrors snapshot details styling) */}
      <TempSnapshotModal
        open={tempModalOpen}
        onClose={closeTempModal}
        tempSnapshot={tempSnapshot}
        tempPrevSnapshot={tempPrevSnapshot}
        fetchCardObject={fetchCardObject}
        cardCache={cardCache}
        getCardName={getCardName}
        formatNumber={formatNumber}
        formatCurrency={formatCurrency}
      />
    </Container>
  )
}
