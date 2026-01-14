import React, { useEffect, useState } from 'react'
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
} from '@mui/material'

interface LeaderboardEntry {
  rank?: number
  user_id?: number
  user_name?: string
  rating?: number
  wins?: number
  losses?: number
}

// Keep the same apiUrl construction used in other pages so developers can set VITE_API_URL
const remoteApi = (import.meta.env.VITE_API_URL as string) || ''
const apiUrl = (path: string) => {
  if (!remoteApi) {
    console.warn('[PreconLeague] VITE_API_URL is not set — falling back to /api (ensure you set VITE_API_URL at build time)')
    return `/api${path}`
  }
  const origin = remoteApi.endsWith('/') ? remoteApi.slice(0, -1) : remoteApi
  return `${origin}/api${path}`
}

export default function Leaderboards() {
  const [data, setData] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchLeaderboards()
  }, [])

  async function fetchLeaderboards() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(apiUrl('/leaderboards/'))
      if (!res.ok) {
        throw new Error(`Failed to fetch leaderboards: ${res.status} ${res.statusText}`)
      }
      const json = await res.json()
      if (!Array.isArray(json)) {
        setData([])
      } else {
        setData(json)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">Leaderboards</Typography>
        <Box>
          <Button component={RouterLink} to="/" variant="outlined" sx={{ mr: 1 }}>Home</Button>
          <Button onClick={fetchLeaderboards} variant="contained">Refresh</Button>
        </Box>
      </Box>

      {loading && <Box my={2}><CircularProgress /></Box>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {!loading && !error && (
        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell>
                <TableCell>Player</TableCell>
                <TableCell align="right">Rating</TableCell>
                <TableCell align="right">Wins</TableCell>
                <TableCell align="right">Losses</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5}>
                    <Typography sx={{ p: 2 }}>No leaderboard data available.</Typography>
                  </TableCell>
                </TableRow>
              )}
              {data.map((row, idx) => (
                <TableRow key={row.user_id ?? idx}>
                  <TableCell>{row.rank ?? idx + 1}</TableCell>
                  <TableCell>{row.user_name ?? `User ${row.user_id ?? 'unknown'}`}</TableCell>
                  <TableCell align="right">{row.rating ?? '-'}</TableCell>
                  <TableCell align="right">{row.wins ?? '-'}</TableCell>
                  <TableCell align="right">{row.losses ?? '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Container>
  )
}
