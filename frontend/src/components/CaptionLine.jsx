const SPEAKER_COLORS = [
  'bg-blue-500', 'bg-purple-500', 'bg-emerald-500', 'bg-orange-500', 'bg-pink-500',
]

function LatencyDot({ ms }) {
  if (ms <= 1000) return <span title={`${ms}ms`}>🟢</span>
  if (ms <= 2000) return <span title={`${ms}ms`}>🟡</span>
  return <span title={`${ms}ms`}>🔴</span>
}

export function CaptionLine({ caption, isLatest }) {
  const { text, timestamp, latency_ms, speaker } = caption
  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
      isLatest
        ? 'bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800'
        : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
    }`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white mt-0.5 ${
        SPEAKER_COLORS[speaker % SPEAKER_COLORS.length]
      }`}>
        {speaker === 0 ? 'S1' : `S${speaker + 1}`}
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-base leading-relaxed ${
          isLatest ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'
        }`}>
          {text}
        </p>
      </div>
      <div className="flex-shrink-0 flex flex-col items-end gap-1 text-xs text-gray-400">
        <span>{timestamp}</span>
        <LatencyDot ms={latency_ms} />
      </div>
    </div>
  )
}