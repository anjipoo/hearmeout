import { Mic, MicOff, Trash2 } from 'lucide-react'

export function Controls({ isCapturing, isConnected, onStart, onStop, onClear, captionCount, micError }) {
  return (
    <div className="border-t border-gray-200 dark:border-gray-800 px-6 py-4">
      {micError && (
        <p className="text-red-500 text-sm mb-3 text-center">⚠️ Mic error: {micError}</p>
      )}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-400">
          {captionCount} {captionCount === 1 ? 'line' : 'lines'}
        </span>
        <div className="flex items-center gap-3">
          <button
            onClick={onClear}
            disabled={captionCount === 0}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            title="Clear captions"
          >
            <Trash2 size={18} />
          </button>
          <button
            onClick={isCapturing ? onStop : onStart}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-full font-semibold text-sm transition-all duration-200 shadow-sm ${
              isCapturing
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isCapturing ? <><MicOff size={16} /> Stop</> : <><Mic size={16} /> Start Listening</>}
          </button>
        </div>
        <span className="w-16" />
      </div>
    </div>
  )
}