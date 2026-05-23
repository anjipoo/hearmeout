const SPEAKER_COLORS = [
  'bg-blue-500', 'bg-purple-500', 'bg-emerald-500', 'bg-orange-500', 'bg-pink-500',
]

function LatencyDot({ ms }) {
  if (ms <= 1000) return <span title={`${ms}ms`}>🟢</span>
  if (ms <= 2000) return <span title={`${ms}ms`}>🟡</span>
  return <span title={`${ms}ms`}>🔴</span>
}

function highlightKeywords(text, keywords) {
  if (!keywords || keywords.length === 0) return text

  // Build a regex that matches any keyword (case-insensitive)
  const escaped = keywords.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const regex = new RegExp(`(${escaped.join('|')})`, 'gi')
  const parts = text.split(regex)

  return parts.map((part, i) =>
    regex.test(part)
      ? <mark key={i} className="bg-yellow-200 dark:bg-yellow-800 text-gray-900 dark:text-yellow-100 rounded px-0.5">{part}</mark>
      : part
  )
}

export function CaptionLine({ caption, isLatest }) {
  const { text, timestamp, latency_ms, speaker, is_question, keywords, action_items } = caption

  return (
    <div className={`
      flex items-start gap-3 px-4 py-3 rounded-xl transition-all duration-300
      ${is_question
        ? 'bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800'
        : isLatest
          ? 'bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800'
          : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
      }
    `}>

      {/* Speaker avatar */}
      <div className={`
        flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
        text-xs font-bold text-white mt-0.5
        ${SPEAKER_COLORS[speaker % SPEAKER_COLORS.length]}
      `}>
        {`S${speaker + 1}`}
      </div>

      {/* Main content */}
      <div className="flex-1 min-w-0 space-y-1">

        {/* Badges row */}
        {(is_question || action_items?.length > 0) && (
          <div className="flex items-center gap-2 flex-wrap">
            {is_question && (
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300">
                ❓ Question
              </span>
            )}
            {action_items?.length > 0 && (
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300">
                ✅ Action Item
              </span>
            )}
          </div>
        )}

        {/* Caption text with keyword highlights */}
        <p className={`
          text-base leading-relaxed
          ${isLatest && !is_question
            ? 'text-gray-900 dark:text-white'
            : 'text-gray-600 dark:text-gray-400'
          }
        `}>
          {highlightKeywords(text, keywords)}
        </p>

        {/* Keywords chip row */}
        {keywords?.length > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
            {keywords.map((kw, i) => (
              <span
                key={i}
                className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-800"
              >
                {kw}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Timestamp + latency */}
      <div className="flex-shrink-0 flex flex-col items-end gap-1 text-xs text-gray-400">
        <span>{timestamp}</span>
        <LatencyDot ms={latency_ms} />
      </div>
    </div>
  )
}