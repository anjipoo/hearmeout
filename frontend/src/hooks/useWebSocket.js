import { useEffect, useRef, useState, useCallback } from 'react'

const WS_URL = 'ws://localhost:8000/ws/audio'

// Connection states
export const WS_STATE = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  ERROR: 'error',
}

export function useWebSocket(onMessage) {
  const wsRef = useRef(null)
  const onMessageRef = useRef(onMessage)
  const [state, setState] = useState(WS_STATE.DISCONNECTED)
  const [sessionId, setSessionId] = useState(null)

  // Keep onMessage ref fresh without re-running the effect
  useEffect(() => { onMessageRef.current = onMessage }, [onMessage])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setState(WS_STATE.CONNECTING)
    const ws = new WebSocket(WS_URL)
    ws.binaryType = 'arraybuffer'
    wsRef.current = ws

    ws.onopen = () => {
      setState(WS_STATE.CONNECTED)
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        // Capture session ID from the first status message
        if (data.type === 'status' && data.session_id) {
          setSessionId(data.session_id)
        }

        onMessageRef.current(data)
      } catch (e) {
        console.error('Failed to parse message:', e)
      }
    }

    ws.onerror = () => setState(WS_STATE.ERROR)

    ws.onclose = () => {
      setState(WS_STATE.DISCONNECTED)
      wsRef.current = null
    }
  }, [])

  const disconnect = useCallback(() => {
    wsRef.current?.close()
    wsRef.current = null
    setSessionId(null)
  }, [])

  // Send raw binary audio chunk to server
  const sendAudio = useCallback((chunk) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(chunk)
    }
  }, [])

  return { state, sessionId, connect, disconnect, sendAudio }
}