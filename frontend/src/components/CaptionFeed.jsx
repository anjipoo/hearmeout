import { useEffect, useRef } from 'react'
import { CaptionLine } from './CaptionLine'

export function CaptionFeed({ captions }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [captions.length])

  if (captions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-gray-400 dark:text-gray-600 space-y-2">
          <p className="text-4xl">🎙️</p>
          <p className="text-lg font-medium">Waiting for speech...</p>
          <p className="text-sm">Press Start and begin speaking</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2 scroll-smooth">
      {captions.map((caption, i) => (
        <CaptionLine
          key={caption.id}
          caption={caption}
          isLatest={i === captions.length - 1}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}