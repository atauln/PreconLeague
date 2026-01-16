import { IconButton, Tooltip } from '@mui/material'
import Brightness7Icon from '@mui/icons-material/Brightness7'
import Brightness4Icon from '@mui/icons-material/Brightness4'
import { useColorMode } from './theme/ThemeProvider'

export default function ThemeToggle() {
  const { mode, toggleMode } = useColorMode()

  return (
    <div style={{ position: 'fixed', right: 12, top: 12, zIndex: 1400 }}>
      <Tooltip title={mode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}>
        <IconButton aria-label="toggle theme" onClick={toggleMode} size="large" sx={{ bgcolor: 'background.paper' }}>
          {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>
      </Tooltip>
    </div>
  )
}
