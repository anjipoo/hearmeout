import { Mic2, Sun, Moon } from 'lucide-react'

export function Header({ theme, onToggleTheme, connectionState, sessionId }) {
  const statusColor = {
    connected: 'bg-green-500',
    connecting: 'bg-yellow-500 animate-pulse',
    disconnected: 'bg-gray-400',
    error: 'bg-red-500',
  }[connectionState]

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800">
      <div className="flex items-center gap-3">
        <Mic2 className="text-blue-500" size={24} />
        <span className="text-xl font-bold tracking-tight">HearMeOut</span>
        {sessionId && (
          <span className="text-xs text-gray-400 font-mono">#{sessionId}</span>
        )}
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span className={`w-2 h-2 rounded-full ${statusColor}`} />
          <span className="capitalize hidden sm:inline">{connectionState}</span>
        </div>
        <button
          onClick={onToggleTheme}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          title="Toggle theme"
        >
          {theme === 'dark'
            ? <Sun size={18} className="text-yellow-400" />
            : <Moon size={18} className="text-gray-600" />}
        </button>
      </div>
    </header>
  )
}