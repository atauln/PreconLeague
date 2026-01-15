import { useEffect, useMemo, useState, useRef, useCallback } from 'react'
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
  Menu,
  IconButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Tabs,
  Tab,
} from '@mui/material'

interface Deck {
  deck_id: number
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

  const containerRef = useRef<HTMLDivElement | null>(null)
  const svgRef = useRef<SVGSVGElement | null>(null)
  const [actualWidth, setActualWidth] = useState<number>(width)
  const [hoverIdx, setHoverIdx] = useState<number | null>(null)
  const [tooltipPos, setTooltipPos] = useState<{ left: number; top: number } | null>(null)

  const ys = data.map((d) => (d.y === null || d.y === undefined ? NaN : d.y))
  const yNumbers = ys.filter((v) => Number.isFinite(v)) as number[]
  const minY = yNumbers.length ? Math.min(...yNumbers) : 0
  const maxY = yNumbers.length ? Math.max(...yNumbers) : 1
  const pad = (maxY - minY) * 0.1 || 1
  const y0 = minY - pad
  const y1 = maxY + pad
  // leave space on left for y-axis labels and add vertical margins to match MultiLineChart
  const leftMargin = 56
  const rightMargin = 12
  const topMargin = 20
  const bottomMargin = 40
  const chartWidth = Math.max(50, actualWidth - leftMargin - rightMargin)
  const chartInnerHeight = Math.max(30, height - topMargin - bottomMargin)
  const chartHeight = height

  const px = (i: number) => (data.length === 1 ? leftMargin + chartWidth / 2 : leftMargin + (i / (data.length - 1)) * chartWidth)
  const py = (v: number) => (topMargin + (1 - (v - y0) / (y1 - y0)) * chartInnerHeight)

  const path = data
    .map((pt, i) => {
      if (pt.y === null || pt.y === undefined) return null
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

  const handlePointerMove = useCallback((e: React.PointerEvent<SVGSVGElement>) => {
    const svg = e.currentTarget
    const rect = svg.getBoundingClientRect()
    const x = e.clientX - rect.left

    // find nearest data point by px
    let nearest: number | null = null
    let nearestDist = Infinity
    for (let i = 0; i < data.length; i++) {
      const xi = px(i)
      const d = Math.abs(x - xi)
      if (d < nearestDist) {
        nearestDist = d
        nearest = i
      }
    }

    if (nearest === null) {
      setHoverIdx(null)
      setTooltipPos(null)
      return
    }

    setHoverIdx(nearest)

    // position tooltip above the point
    const left = px(nearest)
    const yVal = data[nearest].y
    const top = yVal === null || yVal === undefined ? chartHeight / 2 : py(Number(yVal))

    // translate svg coords to container coordinates (container is the Box wrapping the svg)
    if (containerRef.current) {
      const crect = containerRef.current.getBoundingClientRect()
      const svgRect = svg.getBoundingClientRect()
      setTooltipPos({ left: left + svgRect.left - crect.left, top: top + svgRect.top - crect.top })
    } else {
      setTooltipPos({ left, top })
    }
  }, [data, px, py, chartHeight])

  // keep actualWidth in sync with rendered svg width
  useEffect(() => {
    const updateWidth = () => {
      if (svgRef.current) {
        const w = Math.max(0, svgRef.current.getBoundingClientRect().width)
        setActualWidth(w)
      }
    }
    updateWidth()
    window.addEventListener('resize', updateWidth)
    return () => window.removeEventListener('resize', updateWidth)
  }, [])

  const handlePointerLeave = useCallback(() => {
    setHoverIdx(null)
    setTooltipPos(null)
  }, [])

  return (
    <Box sx={{ overflow: 'visible', p: 2, position: 'relative' }} ref={containerRef}>
      <svg ref={svgRef} width="100%" height={height} role="img" aria-label="line chart" onPointerMove={handlePointerMove} onPointerLeave={handlePointerLeave}>
        <rect x={0} y={0} width={actualWidth} height={height} fill="#fff" />
        {/* grid lines + y labels (respect vertical margins) */}
        {tickValues.map((tv, idx) => {
          const t = idx / (ticks - 1)
          const y = topMargin + t * chartInnerHeight
          return (
            <g key={idx}>
              <line x1={leftMargin} x2={leftMargin + chartWidth} y1={y} y2={y} stroke="#eee" />
              <text x={leftMargin - 8} y={y + 4} textAnchor="end" fontSize={12} fill="#666">{new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(tv)}</text>
            </g>
          )
        })}
        {/* path */}
        {path && <path d={path} fill="none" stroke={stroke} strokeWidth={2} />}

        {/* hover marker + highlighted point */}
        {hoverIdx !== null && hoverIdx !== undefined && hoverIdx >= 0 && hoverIdx < data.length && (
          <g>
            <line x1={px(hoverIdx)} x2={px(hoverIdx)} y1={topMargin} y2={topMargin + chartInnerHeight} stroke="rgba(0,0,0,0.12)" strokeWidth={1} />
          </g>
        )}

        {/* points */}
        {data.map((pt, i) => {
          if (pt.y === null || pt.y === undefined) return null
          const v = Number(pt.y)
          if (!Number.isFinite(v)) return null
          const x = px(i)
          const y = py(v)
          const isHover = hoverIdx === i
          return (
            <circle key={i} cx={x} cy={y} r={isHover ? 5 : 3} fill={stroke} stroke={isHover ? '#fff' : 'none'} strokeWidth={isHover ? 1.5 : 0} />
          )
        })}
      </svg>

      {/* tooltip */}
      {hoverIdx !== null && tooltipPos && (
        <Box sx={{ position: 'absolute', pointerEvents: 'none', zIndex: 10 }} style={{ left: tooltipPos.left + 8, top: Math.max(4, tooltipPos.top - 28) }}>
          <Paper sx={{ p: 0.5, minWidth: 88 }} elevation={3}>
            <Box sx={{ px: 1 }}>
                <Typography variant="caption">{data[hoverIdx].x}</Typography>
                <Typography variant="body2">{data[hoverIdx].y === null || data[hoverIdx].y === undefined ? '—' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(Number(data[hoverIdx].y))}</Typography>
            </Box>
          </Paper>
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 2, mt: 1, flexWrap: 'wrap' }}>
        {data.map((d) => (
          <Typography key={d.x} variant="caption">{d.x}</Typography>
        ))}
      </Box>
    </Box>
  )
}

// Multi-line chart: accepts multiple named series and aligns them to a shared x-axis (keys)
function MultiLineChart({
  series,
  width = 900,
  height = 420,
  startYZero = false,
}: {
  series: { name: string; data: { x: string; y: number | null }[]; stroke?: string }[]
  width?: number
  height?: number
  startYZero?: boolean
}) {
  if (!series || series.length === 0) return <Box sx={{ p: 2 }}>No data</Box>

  const containerRef = useRef<HTMLDivElement | null>(null)
  const svgRef = useRef<SVGSVGElement | null>(null)
  const [actualWidth, setActualWidth] = useState<number>(width)
  const [hoverIdx, setHoverIdx] = useState<number | null>(null)
  const [tooltipPos, setTooltipPos] = useState<{ left: number; top: number } | null>(null)

  // compute union of x keys and sort them (W## first by number, then ISO dates)
  const allKeys = Array.from(new Set(series.flatMap((s) => s.data.map((d) => d.x))))
  const parseKey = (k: string) => {
    if (k.startsWith('W')) {
      const n = Number(k.slice(1))
      return { type: 'week', value: n }
    }
    const d = Date.parse(k)
    if (!Number.isNaN(d)) return { type: 'date', value: d }
    return { type: 'other', value: k }
  }
  allKeys.sort((a, b) => {
    const pa = parseKey(a)
    const pb = parseKey(b)
    if (pa.type === 'week' && pb.type === 'week') return Number(pa.value) - Number(pb.value)
    if (pa.type === 'week' && pb.type !== 'week') return -1
    if (pa.type !== 'week' && pb.type === 'week') return 1
    if (pa.type === 'date' && pb.type === 'date') return Number(pa.value) - Number(pb.value)
    return String(pa.value).localeCompare(String(pb.value))
  })

  // align series to allKeys
  const aligned = series.map((s, idx) => {
    const map = new Map(s.data.map((d) => [d.x, d]))
    return { name: s.name, data: allKeys.map((k) => ({ x: k, y: map.get(k)?.y ?? null })), stroke: s.stroke }
  })

  // flatten for y domain
  const ys = aligned.flatMap((s) => s.data.map((d) => (d.y === null || d.y === undefined ? NaN : d.y)))
  const yNumbers = ys.filter((v) => Number.isFinite(v)) as number[]
  const minY = startYZero ? 0 : (yNumbers.length ? Math.min(...yNumbers) : 0)
  const maxY = yNumbers.length ? Math.max(...yNumbers) : 1
  const pad = startYZero ? (maxY - minY) * 0.05 || 1 : (maxY - minY) * 0.1 || 1
  const y0 = startYZero ? 0 : minY - pad
  const y1 = maxY + pad

  const leftMargin = 56
  const rightMargin = 12
  const topMargin = 20
  const bottomMargin = 40
  const chartWidth = Math.max(50, actualWidth - leftMargin - rightMargin)
  const chartInnerHeight = Math.max(30, height - topMargin - bottomMargin)
  const chartHeight = height
  const px = (i: number) => (allKeys.length === 1 ? leftMargin + chartWidth / 2 : leftMargin + (i / (allKeys.length - 1)) * chartWidth)
  const py = (v: number) => (topMargin + (1 - (v - y0) / (y1 - y0)) * chartInnerHeight)

  const colors = ['#1976d2', '#9c27b0', '#ff5722', '#2e7d32', '#0277bd', '#d32f2f', '#6a1b9a', '#f9a825']

  useEffect(() => {
    const updateWidth = () => {
      if (svgRef.current) {
        const w = Math.max(0, svgRef.current.getBoundingClientRect().width)
        setActualWidth(w)
      }
    }
    updateWidth()
    window.addEventListener('resize', updateWidth)
    return () => window.removeEventListener('resize', updateWidth)
  }, [])

  const handlePointerMove = useCallback((e: React.PointerEvent<SVGSVGElement>) => {
    const svg = e.currentTarget
    const rect = svg.getBoundingClientRect()
    const x = e.clientX - rect.left
    // find nearest x index
    let nearest: number | null = null
    let nearestDist = Infinity
    for (let i = 0; i < allKeys.length; i++) {
      const xi = px(i)
      const d = Math.abs(x - xi)
      if (d < nearestDist) {
        nearestDist = d
        nearest = i
      }
    }
    if (nearest === null) {
      setHoverIdx(null)
      setTooltipPos(null)
      return
    }
    setHoverIdx(nearest)
    if (containerRef.current) {
      const crect = containerRef.current.getBoundingClientRect()
      setTooltipPos({ left: px(nearest) + rect.left - crect.left, top: Math.max(4, (py(y1) || 0) + rect.top - crect.top) })
    } else {
      setTooltipPos({ left: px(nearest), top: 0 })
    }
  }, [allKeys, px, py, y1])

  const handlePointerLeave = useCallback(() => {
    setHoverIdx(null)
    setTooltipPos(null)
  }, [])

  return (
    <Box sx={{ overflow: 'visible', p: 2, position: 'relative' }} ref={containerRef}>
      <svg ref={svgRef} width="100%" height={height} role="img" aria-label="multi line chart" onPointerMove={handlePointerMove} onPointerLeave={handlePointerLeave}>
        <rect x={0} y={0} width={actualWidth} height={height} fill="#fff" />
        {/* grid lines + y labels */}
        {Array.from({ length: 5 }).map((_, idx) => {
          const t = idx / 4
          const y = topMargin + t * chartInnerHeight
          const tv = y1 - t * (y1 - y0)
          return (
            <g key={idx}>
              <line x1={leftMargin} x2={leftMargin + chartWidth} y1={y} y2={y} stroke="#eee" />
              <text x={leftMargin - 8} y={y + 4} textAnchor="end" fontSize={12} fill="#666">{new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(tv)}</text>
            </g>
          )
        })}

        {/* series paths */}
        {aligned.map((s, si) => {
          const path = s.data
            .map((pt, i) => {
              if (pt.y === null || pt.y === undefined) return null
              const v = Number(pt.y)
              if (!Number.isFinite(v)) return null
              const x = px(i)
              const y = py(v)
              return `${i === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
            })
            .filter(Boolean)
            .join(' ')
          const color = s.stroke ?? colors[si % colors.length]
          return <path key={si} d={path} fill="none" stroke={color} strokeWidth={2} />
        })}
        {/* vertical guide line on hover */}
        {hoverIdx !== null && hoverIdx !== undefined && (
          <line x1={px(hoverIdx)} x2={px(hoverIdx)} y1={topMargin} y2={topMargin + chartInnerHeight} stroke="rgba(0,0,0,0.12)" strokeWidth={1} />
        )}
        {/* points (for hover target) */}
        {aligned.map((s, si) => {
          const color = s.stroke ?? colors[si % colors.length]
          return s.data.map((pt, i) => {
            if (pt.y === null || pt.y === undefined) return null
            const v = Number(pt.y)
            if (!Number.isFinite(v)) return null
            const x = px(i)
            const y = py(v)
            const isHover = hoverIdx === i
            return <circle key={`${si}-${i}`} cx={x} cy={y} r={isHover ? 5 : 3} fill={color} stroke={isHover ? '#fff' : 'none'} strokeWidth={isHover ? 1.5 : 0} />
          })
        })}
      </svg>

      {/* legend (outside svg) - ordered by current hover value (or latest value when not hovering) */}
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 1 }}>
        {(() => {
          const valueAt = (s: typeof aligned[0]) => {
            if (hoverIdx !== null && hoverIdx !== undefined) {
              const v = s.data[hoverIdx]?.y
              if (v === null || v === undefined) return NaN
              const n = Number(v)
              return Number.isFinite(n) ? n : NaN
            }
            for (let i = s.data.length - 1; i >= 0; i--) {
              const v = s.data[i]?.y
              if (v === null || v === undefined) continue
              const n = Number(v)
              if (Number.isFinite(n)) return n
            }
            return NaN
          }

          const order = aligned.map((s, si) => ({ si, val: valueAt(s) }))
            .sort((a, b) => (Number.isFinite(b.val) ? b.val : -Infinity) - (Number.isFinite(a.val) ? a.val : -Infinity))
            .map((x) => x.si)

          return order.map((si) => {
            const s = aligned[si]
            return (
              <Box key={si} sx={{ display: 'flex', alignItems: 'center', gap: 1, pr: 1, borderRight: '1px solid #eee' }}>
                <Box sx={{ width: 12, height: 8, backgroundColor: s.stroke ?? colors[si % colors.length] }} />
                <Typography variant="caption">{s.name} {(() => { const v = valueAt(s); return Number.isFinite(v) ? `— ${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(v)}` : '' })()}</Typography>
              </Box>
            )
          })
        })()}
      </Box>

      {/* tooltip */}
      {hoverIdx !== null && tooltipPos && (
        <Box sx={{ position: 'absolute', pointerEvents: 'none', zIndex: 10 }} style={{ left: tooltipPos.left + 8, top: Math.max(4, tooltipPos.top - 48) }}>
          <Paper sx={{ p: 0.5, minWidth: 160 }} elevation={3}>
            <Box sx={{ px: 1 }}>
              <Typography variant="caption">{allKeys[hoverIdx]}</Typography>
              {(() => {
                const valueAt = (s: typeof aligned[0]) => {
                  const v = s.data[hoverIdx]?.y
                  return Number.isFinite(Number(v)) ? Number(v) : NaN
                }
                const order = aligned.map((s, si) => ({ si, val: valueAt(s) }))
                  .sort((a, b) => (Number.isFinite(b.val) ? b.val : -Infinity) - (Number.isFinite(a.val) ? a.val : -Infinity))
                  .map((x) => x.si)
                return order.map((si) => {
                  const s = aligned[si]
                  const v = s.data[hoverIdx]?.y
                  return <Typography key={si} variant="body2" sx={{ color: s.stroke ?? colors[si % colors.length] }}>{s.name}: {Number.isFinite(Number(v)) ? new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(Number(v)) : '—'}</Typography>
                })
              })()}
            </Box>
          </Paper>
        </Box>
      )}
    </Box>
  )
}

export default function Analytics() {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loadingDecks, setLoadingDecks] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [selectedDeckId, setSelectedDeckId] = useState<number>(-1)
  const [snapshots, setSnapshots] = useState<Snapshot[]>([])
  const [loadingSnapshots, setLoadingSnapshots] = useState(false)
  const [allDecksSnapshots, setAllDecksSnapshots] = useState<Array<{ deck_id: number; deck_name: string; weekly: Snapshot[] }>>([])
  const [loadingAllDecks, setLoadingAllDecks] = useState(false)
  const [metricIndex, setMetricIndex] = useState(0)

  const [showOverall, setShowOverall] = useState(true)
  const [showBracket, setShowBracket] = useState(true)
  const [showSalt, setShowSalt] = useState(true)
  const [showPowerLevel, setShowPowerLevel] = useState(false)
  const [showSynergy, setShowSynergy] = useState(false)
  const [showThreat, setShowThreat] = useState(false)
  const [showCombo, setShowCombo] = useState(false)
  const [showManabase, setShowManabase] = useState(false)
  const [metricsAnchorEl, setMetricsAnchorEl] = useState<HTMLElement | null>(null)
  const metricsOpen = Boolean(metricsAnchorEl)

  const openMetricsMenu = (e: React.MouseEvent<HTMLElement>) => setMetricsAnchorEl(e.currentTarget)
  const closeMetricsMenu = () => setMetricsAnchorEl(null)

  const getWeekKey = (s: Snapshot) => {
    if (s.week_of_league != null) return `W${s.week_of_league}`
    if (!s.created_at) return `#${s.snapshot_id}`
    const d = new Date(s.created_at)
    const tmp = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
    const dayNum = tmp.getUTCDay() || 7
    tmp.setUTCDate(tmp.getUTCDate() + 4 - dayNum)
    const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(),0,1))
    const weekNo = Math.ceil((((tmp.getTime() - yearStart.getTime()) / 86400000) + 1)/7)
    return `W${weekNo}`
  }

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
      // default to All Decks
      setSelectedDeckId(-1)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoadingDecks(false)
    }
  }

  useEffect(() => {
    if (selectedDeckId === null) return
    if (selectedDeckId === -1) {
      void loadSnapshotsForAllDecks()
    } else {
      void loadSnapshotsForDeck(selectedDeckId)
    }
  }, [selectedDeckId])

  useEffect(() => {
    // if decks list loads and current selection is All Decks, reload all decks snapshots
    if (selectedDeckId === -1 && decks.length > 0) {
      void loadSnapshotsForAllDecks()
    }
  }, [decks])

  async function loadSnapshotsForDeck(deckId: number) {
    setLoadingSnapshots(true)
    setError(null)
    try {
      const res = await fetch(apiUrl(`/snapshots/deck/${deckId}`))
      if (!res.ok) throw new Error(`Snapshots fetch failed: ${res.status}`)
      const json = await res.json()
      const snaps = Array.isArray(json) ? (json as Snapshot[]) : []
      // sort by created_at asc (safely handle missing created_at)
      const sorted = snaps.slice().sort((a: Snapshot, b: Snapshot) => {
        const ta = a.created_at ? new Date(a.created_at).getTime() : 0
        const tb = b.created_at ? new Date(b.created_at).getTime() : 0
        return ta - tb
      })
      // reduce to newest snapshot per week (use week_of_league when present, otherwise derive ISO week from created_at)
      const map = new Map<string, Snapshot>()
      for (const s of sorted) {
        const key = getWeekKey(s)
        map.set(key, s)
      }
      const weekly = Array.from(map.values())
      setSnapshots(weekly)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoadingSnapshots(false)
    }
  }

  async function loadSnapshotsForAllDecks() {
    if (!decks || decks.length === 0) return
    setLoadingAllDecks(true)
    setError(null)
    try {
      const results: Array<{ deck_id: number; deck_name: string; weekly: Snapshot[] }> = []

      // fetch in parallel with a small concurrency limit to avoid overloading the API
      const concurrency = 8
      const batches: Deck[][] = []
      for (let i = 0; i < decks.length; i += concurrency) batches.push(decks.slice(i, i + concurrency))

      for (const batch of batches) {
        const promises = batch.map(async (d) => {
          try {
            const res = await fetch(apiUrl(`/snapshots/deck/${d.deck_id}`))
            if (!res.ok) return null
            const json = await res.json()
            const snaps = Array.isArray(json) ? (json as Snapshot[]) : []
            const sorted = snaps.slice().sort((a: Snapshot, b: Snapshot) => {
              const ta = a.created_at ? new Date(a.created_at).getTime() : 0
              const tb = b.created_at ? new Date(b.created_at).getTime() : 0
              return ta - tb
            })
            const map = new Map<string, Snapshot>()
            for (const s of sorted) {
              const key = getWeekKey(s)
              map.set(key, s)
            }
            const weekly = Array.from(map.values())
            // exclude decks that don't have a W0 or W1 snapshot (treat as outliers)
            const keys = Array.from(map.keys())
            const hasW0orW1 = keys.includes('W0') || keys.includes('W1')
            if (!hasW0orW1) return null
            return { deck_id: d.deck_id, deck_name: d.deck_name, weekly }
          } catch (err) {
            return null
          }
        })

        const settled = await Promise.all(promises)
        for (const r of settled) if (r) results.push(r)
      }

      setAllDecksSnapshots(results)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoadingAllDecks(false)
    }
  }

  // reduce snapshots to the latest snapshot per week (or per day if week is missing)
  const weeklySnapshots = useMemo(() => {
    if (!snapshots || snapshots.length === 0) return [] as Snapshot[]
    // snapshots are sorted by created_at asc; iterate and keep overwriting the key so the map ends
    // with the newest snapshot for each week, while preserving week order.
    const map = new Map<string, Snapshot>()
    for (const s of snapshots) {
      const key = getWeekKey(s)
      map.set(key, s)
    }
    return Array.from(map.values())
  }, [snapshots])

  const overallSeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: s.overall_rating ?? null })), [weeklySnapshots])
  const bracketSeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: s.bracket_rating ?? null })), [weeklySnapshots])
  const saltSeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: s.salt_rating ?? null })), [weeklySnapshots])
  const powerLevelSeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: (s as any).power_level_rating ?? null })), [weeklySnapshots])
  const synergySeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: (s as any).synergy_rating ?? null })), [weeklySnapshots])
  const threatSeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: (s as any).threat_rating ?? null })), [weeklySnapshots])
  const comboSeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: (s as any).combo_rating ?? null })), [weeklySnapshots])
  const manabaseSeries = useMemo(() => weeklySnapshots.map((s) => ({ x: getWeekKey(s), y: (s as any).manabase_score ?? null })), [weeklySnapshots])

  const metrics = [
    { id: 'overall_rating', label: 'Overall Rating' },
    { id: 'bracket_rating', label: 'Bracket Rating' },
    { id: 'salt_rating', label: 'Salt Rating' },
    { id: 'power_level_rating', label: 'Power Level' },
    { id: 'synergy_rating', label: 'Synergy' },
    { id: 'threat_rating', label: 'Threat' },
    { id: 'combo_rating', label: 'Combo' },
    { id: 'manabase_score', label: 'Manabase Score' },
  ]

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
            <MenuItem value={-1}>All Decks</MenuItem>
            {loadingDecks && <MenuItem value="">Loading…</MenuItem>}
            {!loadingDecks && decks.map((d) => (
              <MenuItem key={d.deck_id} value={d.deck_id}>{d.deck_name}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button variant="outlined" onClick={openMetricsMenu}>Metrics ▾</Button>
        <Menu anchorEl={metricsAnchorEl} open={metricsOpen} onClose={closeMetricsMenu} MenuListProps={{ dense: true }}>
          <MenuItem onClick={() => { setShowOverall(!showOverall) }}>
            <ListItemIcon><Checkbox edge="start" checked={showOverall} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Overall</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowBracket(!showBracket) }}>
            <ListItemIcon><Checkbox edge="start" checked={showBracket} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Bracket</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowSalt(!showSalt) }}>
            <ListItemIcon><Checkbox edge="start" checked={showSalt} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Salt</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowPowerLevel(!showPowerLevel) }}>
            <ListItemIcon><Checkbox edge="start" checked={showPowerLevel} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Power Level</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowSynergy(!showSynergy) }}>
            <ListItemIcon><Checkbox edge="start" checked={showSynergy} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Synergy</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowThreat(!showThreat) }}>
            <ListItemIcon><Checkbox edge="start" checked={showThreat} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Threat</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowCombo(!showCombo) }}>
            <ListItemIcon><Checkbox edge="start" checked={showCombo} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Combo</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowManabase(!showManabase) }}>
            <ListItemIcon><Checkbox edge="start" checked={showManabase} tabIndex={-1} disableRipple size="small" /></ListItemIcon>
            <ListItemText>Manabase</ListItemText>
          </MenuItem>
          <Divider />
          <MenuItem onClick={() => { setShowOverall(true); setShowBracket(true); setShowSalt(true); setShowPowerLevel(true); setShowSynergy(true); setShowThreat(true); setShowCombo(true); setShowManabase(true); closeMetricsMenu() }}>
            <ListItemText>Select All</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => { setShowOverall(false); setShowBracket(false); setShowSalt(false); setShowPowerLevel(false); setShowSynergy(false); setShowThreat(false); setShowCombo(false); setShowManabase(false); closeMetricsMenu() }}>
            <ListItemText>Clear All</ListItemText>
          </MenuItem>
        </Menu>
      </Box>

      {loadingSnapshots ? (
        <Box display="flex" justifyContent="center" my={4}><CircularProgress /></Box>
      ) : (
        <>
          {selectedDeckId === -1 ? (
            <Paper sx={{ mb: 2, p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box>
                  <Typography variant="h6">All Decks — Metric view</Typography>
                  <Typography variant="body2" color="text.secondary">Shows the newest snapshot per week for each deck — one metric at a time.</Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <Tabs value={metricIndex} onChange={(_, v) => setMetricIndex(v)} variant="scrollable" scrollButtons="auto" aria-label="metric tabs">
                    {metrics.map((m, i) => (
                      <Tab key={m.id} label={m.label} />
                    ))}
                  </Tabs>
                </Box>
              </Box>

              {loadingAllDecks ? (
                <Box display="flex" justifyContent="center" my={4}><CircularProgress /></Box>
              ) : (
                <Box>
                  {/* build series for current metric */}
                  {allDecksSnapshots.length === 0 ? (
                    <Typography color="text.secondary">No data available for All Decks.</Typography>
                  ) : (
                    <MultiLineChart
                      series={allDecksSnapshots.map((d, idx) => ({
                        name: d.deck_name,
                        data: (() => {
                          // map weekly snapshots to x,y where x is week key (W#)
                          return d.weekly.map((s) => ({ x: getWeekKey(s), y: (s as any)[metrics[metricIndex].id] ?? null }))
                        })(),
                        stroke: undefined,
                      }))}
                      height={520}
                    />
                  )}
                </Box>
              )}
            </Paper>
          ) : (
            <Paper sx={{ mb: 2 }}>
              <Box sx={{ p: 2 }}>
                <Typography variant="h6">Trend charts</Typography>
                <Typography variant="body2" color="text.secondary">Shows historical snapshot metrics for the selected deck.</Typography>
              </Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2, p: 2 }}>
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
                {showPowerLevel && (
                  <Box>
                    <Typography variant="subtitle2">Power Level</Typography>
                    <LineChart data={powerLevelSeries} stroke="#2e7d32" />
                  </Box>
                )}
                {showSynergy && (
                  <Box>
                    <Typography variant="subtitle2">Synergy</Typography>
                    <LineChart data={synergySeries} stroke="#0277bd" />
                  </Box>
                )}
                {showThreat && (
                  <Box>
                    <Typography variant="subtitle2">Threat</Typography>
                    <LineChart data={threatSeries} stroke="#d32f2f" />
                  </Box>
                )}
                {showCombo && (
                  <Box>
                    <Typography variant="subtitle2">Combo</Typography>
                    <LineChart data={comboSeries} stroke="#6a1b9a" />
                  </Box>
                )}
                {showManabase && (
                  <Box>
                    <Typography variant="subtitle2">Manabase Score</Typography>
                    <LineChart data={manabaseSeries} stroke="#f9a825" />
                  </Box>
                )}
              </Box>
            </Paper>
          )}

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Latest snapshot</Typography>
            {snapshots.length === 0 ? (
              <Typography color="text.secondary" sx={{ mt: 1 }}>No snapshots available for this deck.</Typography>
            ) : (
              <Box sx={{ mt: 1 }}>
                <Typography>Most recent: {snapshots[snapshots.length - 1].created_at ?? '—'}</Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 2, mt: 1 }}>
                  <Typography>Overall: {formatNumber(snapshots[snapshots.length - 1].overall_rating)}</Typography>
                  <Typography>Bracket: {formatNumber(snapshots[snapshots.length - 1].bracket_rating)}</Typography>
                  <Typography>Salt: {formatNumber(snapshots[snapshots.length - 1].salt_rating)}</Typography>
                  <Typography>Power Level: {formatNumber((snapshots[snapshots.length - 1] as any).power_level_rating)}</Typography>
                  <Typography>Synergy: {formatNumber((snapshots[snapshots.length - 1] as any).synergy_rating)}</Typography>
                  <Typography>Threat: {formatNumber((snapshots[snapshots.length - 1] as any).threat_rating)}</Typography>
                  <Typography>Combo: {formatNumber((snapshots[snapshots.length - 1] as any).combo_rating)}</Typography>
                  <Typography>Manabase: {formatNumber((snapshots[snapshots.length - 1] as any).manabase_score)}</Typography>
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
