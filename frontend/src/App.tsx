import { useEffect, useState } from 'react'
import { FileText, CheckCircle, Loader2 } from 'lucide-react'

function App() {
  const [message, setMessage] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/')
      .then(res => res.json())
      .then(data => {
        setMessage(data.message)
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setMessage('Backend not connected yet')
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800 rounded-2xl shadow-2xl p-8 border border-slate-700">
        <div className="flex justify-center mb-6">
          <div className="bg-blue-500/20 p-4 rounded-full">
            <FileText className="w-12 h-12 text-blue-400" />
          </div>
        </div>

        <h1 className="text-2xl font-bold text-center mb-2 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          BTS Contract Automation
        </h1>
        <p className="text-slate-400 text-center mb-8">
          Hệ thống soạn thảo phụ lục tự động
        </p>

        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-slate-700/50 rounded-xl border border-slate-600">
            {loading ? (
              <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
            ) : (
              <CheckCircle className="w-5 h-5 text-green-400" />
            )}
            <span className="text-sm font-medium">
              {loading ? 'Đang kết nối backend...' : 'Backend Status: Online'}
            </span>
          </div>

          <div className="p-4 bg-blue-500/10 rounded-xl border border-blue-500/20 text-blue-300 text-sm">
            <p className="font-semibold mb-1">Tin nhắn từ server:</p>
            <p className="italic">"{message || '...'}"</p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-700">
          <div className="flex justify-between text-xs text-slate-500">
            <span>Version: 1.0.0 (Production)</span>
            <span>By: Antigravity</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
