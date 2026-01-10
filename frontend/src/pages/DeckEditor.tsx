import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'

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

  if (!deckId || isNaN(id)) {
    return (
      <main style={{ padding: 16 }}>
        <p>Invalid deck id. <Link to="/">Back</Link></p>
      </main>
    )
  }

  return (
    <main style={{ padding: 16 }}>
      <h1>Deck editor</h1>
      <p>
        <Link to="/">← Back to home</Link>
      </p>

      {loading && <p>Loading…</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {deck && (
        <section style={{ marginTop: 12 }}>
          <h2>{deck.deck_name}</h2>
          <div>Owner id: {deck.user_id}</div>
          <div>Source: {deck.source}</div>
          {deck.moxfield_deck_url && (
            <div>
              <a href={deck.moxfield_deck_url} target="_blank" rel="noreferrer">View Moxfield</a>
            </div>
          )}
          {deck.archidekt_deck_url && (
            <div>
              <a href={deck.archidekt_deck_url} target="_blank" rel="noreferrer">View Archidekt</a>
            </div>
          )}
        </section>
      )}

      <section style={{ marginTop: 20 }}>
        <h3>Snapshots</h3>
        <div style={{ marginBottom: 8 }}>
          <button onClick={handleCreateSnapshot} disabled={creating || loading}>
            {creating ? 'Creating snapshot…' : 'Create snapshot from source'}
          </button>
        </div>
        {snapshots.length === 0 && <p>No snapshots yet.</p>}
        <ul>
          {snapshots.map((s) => (
            <li key={s.snapshot_id} style={{ padding: 8, border: '1px solid #eee', marginBottom: 6 }}>
              <div>
                <strong>{s.snapshot_name || `Snapshot ${s.snapshot_id}`}</strong>
              </div>
              <div style={{ fontSize: 12, color: '#666' }}>{s.created_at}</div>
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
