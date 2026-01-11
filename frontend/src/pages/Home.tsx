import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface Deck {
  deck_id: number
  user_id: number
  moxfield_deck_url?: string | null
  archidekt_deck_url?: string | null
  source: string
  deck_name: string
}
// Build API URL correctly for both local proxied development and remote API.
// - If VITE_API_URL is set (e.g. https://preconleague.cs.house) we'll call
//   `${VITE_API_URL}/decks/...` (no extra /api prefix). Otherwise we use the
//   local dev-server proxy path `/api/decks/...` which forwards to your local
//   backend (see vite.config.ts).
const remoteApi = (import.meta.env.VITE_API_URL as string) || ''
const apiUrl = (path: string) => (remoteApi ? `${remoteApi}${path}` : `/api${path}`)

export default function Home() {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [source, setSource] = useState<'moxfield' | 'archidekt'>('moxfield')
  const [deckUrl, setDeckUrl] = useState('')
  const [creating, setCreating] = useState(false)
  const [createMessage, setCreateMessage] = useState<string | null>(null)

  useEffect(() => {
    fetchDecks()
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
      setDecks(data || [])
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
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
      // Refresh list
      fetchDecks()
    } catch (err: unknown) {
      setCreateMessage(`Error: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setCreating(false)
    }
  }

  return (
    <main className="container mx-auto py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold">Precon League — Home</h1>
        <p className="muted">Choose a deck to edit (this demo is unauthenticated — any user can open any deck).</p>
      </header>

      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium">All decks</h2>
        </div>
        {loading && <p>Loading decks…</p>}
        {error && <p className="text-red-600">{error}</p>}
        {!loading && !error && (
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {decks.length === 0 && <li>No decks found.</li>}
            {decks.map((d) => (
              <li key={d.deck_id} className="card flex items-center justify-between">
                <div>
                  <div className="text-lg font-semibold">{d.deck_name}</div>
                  <div className="muted">owner id: {d.user_id} • source: {d.source}</div>
                </div>
                <div className="flex items-center gap-3">
                  {d.moxfield_deck_url && (
                    <a className="muted" href={d.moxfield_deck_url} target="_blank" rel="noreferrer">View source</a>
                  )}
                  {d.archidekt_deck_url && (
                    <a className="muted" href={d.archidekt_deck_url} target="_blank" rel="noreferrer">View source</a>
                  )}
                  <Link to={`/decks/${d.deck_id}`} className="btn">Edit</Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="text-lg font-medium mb-2">Create or register a deck</h2>
        <p className="muted">Provide an Archidekt or Moxfield deck URL and click Submit to register it into the league.</p>
        <form onSubmit={handleCreate} className="mt-3 grid grid-cols-1 md:grid-cols-6 gap-3 items-center">
          <div className="md:col-span-1">
            <label className="block text-sm">Source</label>
            <select value={source} onChange={(e) => setSource(e.target.value as 'moxfield' | 'archidekt')} className="input">
              <option value="moxfield">Moxfield</option>
              <option value="archidekt">Archidekt</option>
            </select>
          </div>
          <div className="md:col-span-4">
            <label className="block text-sm">URL</label>
            <input
              type="url"
              value={deckUrl}
              onChange={(e) => setDeckUrl(e.target.value)}
              placeholder="https://moxfield.com/decks..."
              required
              className="input"
            />
          </div>
          <div className="md:col-span-1">
            <label className="block text-sm">&nbsp;</label>
            <button type="submit" disabled={creating} className="btn w-full">
              {creating ? 'Creating…' : 'Submit'}
            </button>
          </div>
        </form>
        {createMessage && <p className="mt-2 muted">{createMessage}</p>}
      </section>
    </main>
  )
}
