import { useRef, useState, useCallback } from 'react'

const SAMPLE_RATE = 16000
const CHUNK_MS = 30
const CHUNK_SAMPLES = (SAMPLE_RATE * CHUNK_MS) / 1000  // 480 samples

export function useMicrophone(onChunk) {
  const onChunkRef = useRef(onChunk)
  const streamRef = useRef(null)
  const contextRef = useRef(null)
  const processorRef = useRef(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [error, setError] = useState(null)

  // Keep onChunk ref fresh
  useRef(() => { onChunkRef.current = onChunk })

  const start = useCallback(async () => {
    try {
      setError(null)

      // Request mic — browser will prompt for permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: SAMPLE_RATE,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        }
      })

      streamRef.current = stream

      // AudioContext resamples to our target rate
      const context = new AudioContext({ sampleRate: SAMPLE_RATE })
      contextRef.current = context

      const source = context.createMediaStreamSource(stream)

      // ScriptProcessor gives us raw PCM frames
      // 4096 buffer size is the smallest reliable cross-browser value
      const processor = context.createScriptProcessor(4096, 1, 1)
      processorRef.current = processor

      // Accumulate samples until we have a full 30ms chunk
      let buffer = new Float32Array(0)

      processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0)

        // Append new samples to buffer
        const combined = new Float32Array(buffer.length + input.length)
        combined.set(buffer)
        combined.set(input, buffer.length)
        buffer = combined

        // Emit complete chunks
        while (buffer.length >= CHUNK_SAMPLES) {
          const chunk = buffer.slice(0, CHUNK_SAMPLES)
          buffer = buffer.slice(CHUNK_SAMPLES)

          // Convert Float32 [-1, 1] → Int16 PCM (what the backend expects)
          const int16 = new Int16Array(CHUNK_SAMPLES)
          for (let i = 0; i < CHUNK_SAMPLES; i++) {
            int16[i] = Math.max(-32768, Math.min(32767, chunk[i] * 32768))
          }

          onChunkRef.current(int16.buffer)
        }
      }

      source.connect(processor)
      processor.connect(context.destination)

      setIsCapturing(true)
    } catch (err) {
      setError(err.message)
      console.error('Microphone error:', err)
    }
  }, [])

  const stop = useCallback(() => {
    processorRef.current?.disconnect()
    processorRef.current = null

    contextRef.current?.close()
    contextRef.current = null

    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null

    setIsCapturing(false)
  }, [])

  return { isCapturing, error, start, stop }
}