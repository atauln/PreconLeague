import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import DeckEditor from './pages/DeckEditor'
import Admin from './pages/Admin'
import Leaderboards from './pages/Leaderboards'

function App() {
  const basename = (import.meta.env.BASE_URL as string) || '/'
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/decks/:deckId" element={<DeckEditor />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/leaderboards" element={<Leaderboards />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
