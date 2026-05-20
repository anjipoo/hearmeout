import { useState, useCallback, useEffect } from 'react'
import { useWebSocket, WS_STATE } from './hooks/useWebSocket'
import { useMicrophone } from './hooks/useMicrophone'
import { Header } from './components/Header'
import { CaptionFeed } from './components/CaptionFeed'
import { Controls } from './components/Controls'

// Format Date → "HH:MM:SS"
function formatTime(date) {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

let captionIdCounter = 0

export default function App() {
  const [theme, setTheme] = useState('dark')
  const [captions, setCaptions] = useState([])

  // Apply theme class to <html>
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((data) => {
    if (data.type === 'transcript' && data.text) {
      setCaptions(prev => [...prev, {
        id: captionIdCounter++,
        text: data.text,
        timestamp: formatTime(new Date()),
        latency_ms: data.latency_ms ?? 0,
        speaker: 0,   // Phase 5 will populate this from diarization
      }])
    }
  }, [])

  const { state: wsState, sessionId, connect, disconnect, sendAudio } = useWebSocket(handleMessage)
  const { isCapturing, error: micError, start: startMic, stop: stopMic } = useMicrophone(sendAudio)

  const handleStart = useCallback(async () => {
    connect()
    // Small delay to let WebSocket handshake complete before mic starts
    await new Promise(r => setTimeout(r, 300))
    await startMic()
  }, [connect, startMic])

  const handleStop = useCallback(() => {
    stopMic()
    disconnect()
  }, [stopMic, disconnect])

  const handleClear = useCallback(() => setCaptions([]), [])

  return (
    <div className="h-screen flex flex-col bg-white dark:bg-gray-950 text-gray-900 dark:text-white transition-colors duration-200">

      {/* TOP: Header with controls */}
      <Header
        theme={theme}
        onToggleTheme={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
        connectionState={wsState}
        sessionId={sessionId}
      />

      {/* MIDDLE: Caption feed — flex-1 fills remaining space */}
      <CaptionFeed captions={captions} />

      {/* BOTTOM: Start/Stop controls */}
      <Controls
        isCapturing={isCapturing}
        isConnected={wsState === WS_STATE.CONNECTED}
        onStart={handleStart}
        onStop={handleStop}
        onClear={handleClear}
        captionCount={captions.length}
        micError={micError}
      />
    </div>
  )
}