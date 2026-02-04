import type { Dispatch, JSX, SetStateAction } from 'react'
import {
  Box,
  Button,
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
  Typography,
  TextField,
  MenuItem,
  Grid
} from '@mui/material'
import CardImageTooltip from '../components/CardImageTooltip'

type Snapshot = {
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

type ChangedCard = { card_id?: string | null; card_name?: string | null; quantity: number }

export function SnapshotDetailsModal(props: {
  open: boolean
  onClose: () => void
  snapshot: Snapshot | null
  snapshots: Snapshot[]
  cardCache: Record<string, any>
  fetchCardObject: (id: string) => any | null
  getCardName: (id?: string | null) => string
  renderStatWithPrevDiff: (
    snap: Snapshot,
    statKey: keyof Snapshot,
    formatter: (v?: number | null) => string,
    options?: { percent?: boolean; maximumFractionDigits?: number; compareWeek?: number | null }
  ) => JSX.Element
  formatNumber: (v?: number | null, maximumFractionDigits?: number) => string
  formatCurrency: (v?: number | null) => string
  weekEdits: Record<number, number>
  setWeekEdits: Dispatch<SetStateAction<Record<number, number>>>
  modalEditingWeek: boolean
  setModalEditingWeek: (v: boolean) => void
  handleUpdateWeek: (snapshotId: number) => Promise<void>
  updatingWeek: Record<number, boolean>
  compareWeek: number | null
  setCompareWeek: (n: number | null) => void
  changedCards: { added: ChangedCard[]; removed: ChangedCard[] } | null
  changedCardsLoading: boolean
  getQuantityofChangedCards: (changes: { added: ChangedCard[]; removed: ChangedCard[] }) => number
}) {
  const {
    open,
    onClose,
    snapshot,
    snapshots,
    cardCache,
    fetchCardObject,
    getCardName,
    renderStatWithPrevDiff,
    weekEdits,
    setWeekEdits,
    modalEditingWeek,
    setModalEditingWeek,
    handleUpdateWeek,
    updatingWeek,
    compareWeek,
    setCompareWeek,
    changedCards,
    changedCardsLoading,
    getQuantityofChangedCards,
  } = props

  // local aliases for consistency
  const fmtNum = (v?: number | null, mfd = 1) => (props as any).formatNumber ? (props as any).formatNumber(v, mfd) : (v === null || v === undefined ? '—' : String(v))

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>{snapshot ? snapshot.snapshot_name || `Snapshot ${snapshot.snapshot_id}` : 'Snapshot Details'}</Box>
          <Box>
            <TextField
              size="small"
              select
              label="Compare Week"
              value={compareWeek === null ? 'auto' : compareWeek}
              onChange={(e) => {
                const val = e.target.value
                if (val === 'auto') setCompareWeek(null)
                else setCompareWeek(Number(val))
              }}
              sx={{ minWidth: 160 }}
            >
              <MenuItem value="auto">Auto (previous week)</MenuItem>
              {Array.from(new Set(snapshots.map((s) => s.week_of_league).filter((w) => w !== undefined && w !== null && w >= 0)))
                .sort((a: number, b: number) => (b as number) - (a as number))
                .map((wk) => (
                  <MenuItem key={wk} value={wk as number}>{`Week ${wk}`}</MenuItem>
                ))}
            </TextField>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        {snapshot && (
          <Table size="small">
            <TableBody>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>Commander</TableCell>
                <TableCell>{getCardName(snapshot.commander_id)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Overall Rating</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'overall_rating', (v) => fmtNum(v, 1), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Power Level</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'power_level_rating', (v) => fmtNum(v, 2), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Salt Rating</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'salt_rating', (v) => fmtNum(v, 1), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Synergy</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'synergy_rating', (v) => fmtNum(v, 1), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Bracket</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'bracket_rating', (v) => fmtNum(v, 2), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Manabase Score</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'manabase_score', (v) => fmtNum(v, 0), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Commander Tier</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'commander_tier', (v) => fmtNum(v, 0), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Card Quality</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'card_quality', (v) => fmtNum(v, 1), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Archetype</TableCell>
                <TableCell>{snapshot.archetype_major} - {snapshot.archetype_minor}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Price</TableCell>
                <TableCell>{renderStatWithPrevDiff(snapshot, 'price_usd', (v) => (v === null || v === undefined ? '—' : `$${v.toFixed(2)}`), { percent: true, maximumFractionDigits: 2, compareWeek })}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Week</TableCell>
                <TableCell>
                  {!modalEditingWeek ? (
                    <Box display="flex" alignItems="center">
                      <Typography sx={{ mr: 1 }}>{snapshot.week_of_league}</Typography>
                      <Button size="small" onClick={() => setModalEditingWeek(true)}>EDIT</Button>
                    </Box>
                  ) : (
                    <Box display="flex" alignItems="center">
                      <TextField
                        type="number"
                        size="small"
                        inputProps={{ min: 0 }}
                        sx={{ width: 100, mr: 1 }}
                        value={weekEdits[snapshot.snapshot_id] ?? snapshot.week_of_league}
                        onChange={(e) => setWeekEdits((prev) => ({ ...prev, [snapshot.snapshot_id]: Number(e.target.value) }))}
                      />
                      <Button size="small" onClick={() => void handleUpdateWeek(snapshot.snapshot_id)} disabled={!!updatingWeek[snapshot.snapshot_id]}>
                        {updatingWeek[snapshot.snapshot_id] ? 'Updating…' : 'Update'}
                      </Button>
                      <Button size="small" onClick={() => { setModalEditingWeek(false); setWeekEdits((prev) => ({ ...prev, [snapshot.snapshot_id]: snapshot.week_of_league })) }} sx={{ ml: 1 }}>Cancel</Button>
                    </Box>
                  )}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Library changes</TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2" sx={{ mb: 1 }}>[{changedCards?.added.length ?? 0} added]</Typography>
                    {changedCardsLoading ? (
                      <Box display="flex" justifyContent="center"><CircularProgress size={18} /></Box>
                    ) : changedCards ? (
                      <Grid container spacing={2}>
                        <Grid>
                          <Typography sx={{ fontWeight: 'bold' }}>Added</Typography>
                          {changedCards.added.length === 0 ? (
                            <Typography color="text.secondary">None</Typography>
                          ) : (
                            <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                              {changedCards.added.map((card, i) => {
                                const cardId = card.card_id ?? null
                                const fetched = cardId ? fetchCardObject(cardId) : null
                                const cached = cardId ? cardCache[cardId] : null
                                const cardName = card.card_name ?? (fetched?.name ?? cached?.name ?? cardId)
                                const key = `added-${cardId || cardName}-${i}`
                                const qty = Number.isInteger(card.quantity as number) && (card.quantity as number) > 0 ? (card.quantity as number) : 1
                                const displayQty = Math.min(qty, 8)
                                const priceStr = fetched?.prices?.usd ?? cached?.prices?.usd ?? null
                                const priceNum = priceStr ? parseFloat(priceStr as string) : null
                                const isImportant = priceNum !== null && !Number.isNaN(priceNum) && priceNum > 7

                                return (
                                  <Box key={key} display="flex" gap={1} alignItems="center">
                                    {Array.from({ length: displayQty }).map((_, idx) => {
                                      const imgKey = `${key}-img-${idx}`
                                      return (
                                        <CardImageTooltip
                                          key={imgKey}
                                          cardId={cardId}
                                          cardName={cardName}
                                          isImportant={isImportant}
                                          thumbHeight={64}
                                        />
                                      )
                                    })}
                                  </Box>
                                )
                              })}
                            </Box>
                          )}
                        </Grid>
                        <Grid>
                          <Typography sx={{ fontWeight: 'bold' }}>Removed</Typography>
                          {changedCards.removed.length === 0 ? (
                            <Typography color="text.secondary">None</Typography>
                          ) : (
                            <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                              {changedCards.removed.map((card, i) => {
                                const cardId = card.card_id ?? null
                                const fetched = cardId ? fetchCardObject(cardId) : null
                                const cached = cardId ? cardCache[cardId] : null
                                const cardName = card.card_name ?? (fetched?.name ?? cached?.name ?? cardId)
                                const key = `removed-${cardId || cardName}-${i}`
                                const qty = Number.isInteger(card.quantity as number) && (card.quantity as number) > 0 ? (card.quantity as number) : 1
                                const displayQty = Math.min(qty, 8)
                                const priceStr = fetched?.prices?.usd ?? cached?.prices?.usd ?? null
                                const priceNum = priceStr ? parseFloat(priceStr as string) : null
                                const isImportant = priceNum !== null && !Number.isNaN(priceNum) && priceNum > 7

                                return (
                                  <Box key={key} display="flex" gap={1} alignItems="center">
                                    {Array.from({ length: displayQty }).map((_, idx) => {
                                      const imgKey = `${key}-img-${idx}`
                                      return (
                                        <CardImageTooltip
                                          key={imgKey}
                                          cardId={cardId}
                                          cardName={cardName}
                                          isImportant={isImportant}
                                          thumbHeight={64}
                                        />
                                      )
                                    })}
                                  </Box>
                                )
                              })}
                            </Box>
                          )}
                        </Grid>
                      </Grid>
                    ) : (
                      <Typography color="text.secondary">No comparison snapshot available</Typography>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        )}

        
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}

export function TempSnapshotModal(props: {
  open: boolean
  onClose: () => void
  tempSnapshot: any | null
  tempPrevSnapshot: any | null
  fetchCardObject: (id: string) => any | null
  cardCache: Record<string, any>
  getCardName: (id?: string | null) => string
  formatNumber: (v?: number | null, maximumFractionDigits?: number) => string
  formatCurrency: (v?: number | null) => string
}) {
  const { open, onClose, tempSnapshot, tempPrevSnapshot, fetchCardObject, cardCache, getCardName, formatNumber, formatCurrency } = props

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>{tempSnapshot ? tempSnapshot.snapshot_name || 'Temporary Snapshot Preview' : 'Temporary Snapshot Preview'}</Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Preview — not saved</Typography>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        {tempSnapshot ? (
          <>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>Commander</TableCell>
                  <TableCell>{getCardName((tempSnapshot as any).commander_id)}</TableCell>
                </TableRow>
                {(
                  [
                    { key: 'overall_rating', label: 'Overall Rating', fmt: (v: any) => formatNumber(v, 1) },
                    { key: 'power_level_rating', label: 'Power Level', fmt: (v: any) => formatNumber(v, 2) },
                    { key: 'salt_rating', label: 'Salt Rating', fmt: (v: any) => formatNumber(v, 1) },
                    { key: 'synergy_rating', label: 'Synergy', fmt: (v: any) => formatNumber(v, 1) },
                    { key: 'bracket_rating', label: 'Bracket', fmt: (v: any) => formatNumber(v, 2) },
                    { key: 'manabase_score', label: 'Manabase Score', fmt: (v: any) => formatNumber(v, 0) },
                    { key: 'commander_tier', label: 'Commander Tier', fmt: (v: any) => formatNumber(v, 0) },
                    { key: 'card_quality', label: 'Card Quality', fmt: (v: any) => formatNumber(v, 1) },
                    { key: 'price_usd', label: 'Price', fmt: (v: any) => formatCurrency(v) }
                  ] as Array<any>
                ).map((m) => {
                  const tempVal = (tempSnapshot as any)[m.key] as number | null
                  const prevVal = tempPrevSnapshot ? (tempPrevSnapshot as any)[m.key] as number | null : null
                  const formatted = m.fmt(tempVal)

                  if (prevVal === null || prevVal === undefined || Number.isNaN(prevVal as number) || tempVal === null || tempVal === undefined || Number.isNaN(tempVal as number)) {
                    return (
                      <TableRow key={m.key}>
                        <TableCell sx={{ fontWeight: 'bold' }}>{m.label}</TableCell>
                        <TableCell>{formatted}</TableCell>
                      </TableRow>
                    )
                  }

                  const diff = (tempVal as number) - (prevVal as number)
                  const diffFormatted = m.fmt(diff)
                  let percentStr: string | null = null
                  if (prevVal !== 0) {
                    const pct = (diff / (prevVal as number)) * 100
                    const pctFormatter = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2, minimumFractionDigits: 0 })
                    percentStr = `${pctFormatter.format(Math.abs(pct))}%`
                  }

                  return (
                    <TableRow key={m.key}>
                      <TableCell sx={{ fontWeight: 'bold' }}>{m.label}</TableCell>
                      <TableCell>
                        {formatted}
                        <Typography component="span" sx={{ ml: 1, color: diff >= 0 ? 'success.main' : 'error.main', fontSize: '0.875rem' }}>
                          ({diff > 0 ? '+' : ''}{diffFormatted}{percentStr ? ` / ${percentStr}` : ''})
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )
                })}
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Archetype</TableCell>
                  <TableCell>{(tempSnapshot as any).archetype_major} - {(tempSnapshot as any).archetype_minor}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Price</TableCell>
                  <TableCell>{formatCurrency((tempSnapshot as any).price_usd)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Week</TableCell>
                  <TableCell>{(tempSnapshot as any).week_of_league ?? '—'}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
            <Box mt={2}>
              <Typography variant="subtitle1">Library changes [{(tempSnapshot as any).added_cards.length}]</Typography>
              <Box mt={1}>
                {((tempSnapshot as any).added_cards || []).length === 0 && ((tempSnapshot as any).removed_cards || []).length === 0 ? (
                  <Typography color="text.secondary">No changes detected from most recent saved snapshot</Typography>
                ) : (
                  <Grid container spacing={2}>
                    <Grid>
                      <Typography sx={{ fontWeight: 'bold' }}>Added</Typography>
                      {((tempSnapshot as any).added_cards || []).length === 0 ? (
                        <Typography color="text.secondary">None</Typography>
                      ) : (
                        <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                          {((tempSnapshot as any).added_cards || []).map((card: any, i: number) => {
                            const cardId = card.card_id ?? null
                            const fetched = cardId ? fetchCardObject(cardId) : null
                            const cached = cardId ? cardCache[cardId] : null
                            const cardName = card.card_name ?? (fetched?.name ?? cached?.name ?? cardId)
                            const key = `temp-added-${cardId || cardName}-${i}`
                            const qty = Number.isInteger(card.quantity as number) && (card.quantity as number) > 0 ? (card.quantity as number) : 1
                            const displayQty = Math.min(qty, 8)
                            const priceStr = fetched?.prices?.usd ?? cached?.prices?.usd ?? null
                            const priceNum = priceStr ? parseFloat(priceStr as string) : null
                            const isImportant = priceNum !== null && !Number.isNaN(priceNum) && priceNum > 7

                            return (
                              <Box key={key} display="flex" gap={1} alignItems="center">
                                {Array.from({ length: displayQty }).map((_, idx) => {
                                  const imgKey = `${key}-img-${idx}`
                                  return (
                                    <CardImageTooltip
                                      key={imgKey}
                                      cardId={cardId}
                                      cardName={cardName}
                                      isImportant={isImportant}
                                      thumbHeight={80}
                                    />
                                  )
                                })}
                              </Box>
                            )
                          })}
                        </Box>
                      )}
                    </Grid>
                    <Grid>
                      <Typography sx={{ fontWeight: 'bold' }}>Removed</Typography>
                      {((tempSnapshot as any).removed_cards || []).length === 0 ? (
                        <Typography color="text.secondary">None</Typography>
                      ) : (
                        <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                          {((tempSnapshot as any).removed_cards || []).map((card: any, i: number) => {
                            const cardId = card.card_id ?? null
                            const fetched = cardId ? fetchCardObject(cardId) : null
                            const cached = cardId ? cardCache[cardId] : null
                            const cardName = card.card_name ?? (fetched?.name ?? cached?.name ?? cardId)
                            const key = `temp-removed-${cardId || cardName}-${i}`
                            const qty = Number.isInteger(card.quantity as number) && (card.quantity as number) > 0 ? (card.quantity as number) : 1
                            const displayQty = Math.min(qty, 8)
                            const priceStr = fetched?.prices?.usd ?? cached?.prices?.usd ?? null
                            const priceNum = priceStr ? parseFloat(priceStr as string) : null
                            const isImportant = priceNum !== null && !Number.isNaN(priceNum) && priceNum > 7

                            return (
                              <Box key={key} display="flex" gap={1} alignItems="center">
                                {Array.from({ length: displayQty }).map((_, idx) => {
                                  const imgKey = `${key}-img-${idx}`
                                  return (
                                    <CardImageTooltip
                                      key={imgKey}
                                      cardId={cardId}
                                      cardName={cardName}
                                      isImportant={isImportant}
                                      thumbHeight={80}
                                    />
                                  )
                                })}
                              </Box>
                            )
                          })}
                        </Box>
                      )}
                    </Grid>
                  </Grid>
                )}
              </Box>
            </Box>
          </>
        ) : (
          <Box display="flex" justifyContent="center"><CircularProgress /></Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}

export default SnapshotDetailsModal
