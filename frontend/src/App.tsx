import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import DeckEditor from './pages/DeckEditor'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/PreconLeague/" element={<Home />} />
        <Route path="/PreconLeague/decks/:deckId" element={<DeckEditor />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
