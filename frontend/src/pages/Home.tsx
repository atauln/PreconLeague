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
    <main style={{ padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <h1>Precon League — Home</h1>
      <p>
        Choose a deck to edit (this demo is unauthenticated — any user can open any
        deck).
      </p>

      <section style={{ marginTop: 20 }}>
        <h2>All decks</h2>
        {loading && <p>Loading decks…</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {!loading && !error && (
          <ul style={{ paddingLeft: 0, listStyle: 'none' }}>
            {decks.length === 0 && <li>No decks found.</li>}
            {decks.map((d) => (
              <li
                key={d.deck_id}
                style={{
                  padding: 12,
                  border: '1px solid #ddd',
                  borderRadius: 6,
                  marginBottom: 8,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <div>
                    <strong>{d.deck_name}</strong>
                    <div style={{ fontSize: 12, color: '#555' }}>
                      owner id: {d.user_id} • source: {d.source}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    {d.moxfield_deck_url && (
                      <a href={d.moxfield_deck_url} target="_blank" rel="noreferrer">
                        View source
                      </a>
                    )}
                    {d.archidekt_deck_url && (
                      <a href={d.archidekt_deck_url} target="_blank" rel="noreferrer">
                        View source
                      </a>
                    )}
                    <Link to={`/decks/${d.deck_id}`}>
                      <button>Edit</button>
                    </Link>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section style={{ marginTop: 28 }}>
        <h2>Create or register a deck</h2>
        <p style={{ marginTop: 0 }}>
          Provide an Archidekt or Moxfield deck URL and click Submit to register it
          into the league.
        </p>
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label>
            Source:{' '}
            <select value={source} onChange={(e) => setSource(e.target.value as 'moxfield' | 'archidekt')}>
              <option value="moxfield">Moxfield</option>
              <option value="archidekt">Archidekt</option>
            </select>
          </label>
          <label style={{ flex: 1 }}>
            URL:{' '}
            <input
              type="url"
              value={deckUrl}
              onChange={(e) => setDeckUrl(e.target.value)}
              placeholder="https://moxfield.com/decks/..."
              style={{ width: '100%' }}
              required
            />
          </label>
          <button type="submit" disabled={creating}>
            {creating ? 'Creating…' : 'Submit'}
          </button>
        </form>
        {createMessage && <p style={{ marginTop: 8 }}>{createMessage}</p>}
      </section>
    </main>
  )
}
