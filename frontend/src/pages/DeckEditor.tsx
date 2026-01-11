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
      <main className="container mx-auto py-8">
        <p>Invalid deck id. <Link to="/" className="text-sky-600">Back</Link></p>
      </main>
    )
  }

  return (
    <main className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Deck editor</h1>
        <Link to="/" className="muted">← Back to home</Link>
      </div>

      {loading && <p>Loading…</p>}
      {error && <p className="text-red-600">{error}</p>}

      {deck && (
        <section className="card mb-4">
          <h2 className="text-lg font-medium">{deck.deck_name}</h2>
          <div className="muted">Owner id: {deck.user_id}</div>
          <div className="muted">Source: {deck.source}</div>
          <div className="mt-2">
            {deck.moxfield_deck_url && (
              <a className="muted mr-3" href={deck.moxfield_deck_url} target="_blank" rel="noreferrer">View Moxfield</a>
            )}
            {deck.archidekt_deck_url && (
              <a className="muted" href={deck.archidekt_deck_url} target="_blank" rel="noreferrer">View Archidekt</a>
            )}
          </div>
        </section>
      )}

      <section>
        <h3 className="text-lg font-medium mb-2">Snapshots</h3>
        <div className="mb-3">
          <button onClick={handleCreateSnapshot} disabled={creating || loading} className="btn">
            {creating ? 'Creating snapshot…' : 'Create snapshot from source'}
          </button>
        </div>
        {snapshots.length === 0 && <p>No snapshots yet.</p>}
        <ul className="grid gap-3">
          {snapshots.map((s) => (
            <li key={s.snapshot_id} className="card">
              <div>
                <strong>{s.snapshot_name || `Snapshot ${s.snapshot_id}`}</strong>
              </div>
              <div className="muted">{s.created_at}</div>
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
