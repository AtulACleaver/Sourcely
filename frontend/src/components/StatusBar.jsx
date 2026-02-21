import { useEffect, useState } from 'react'
import { checkHealth, checkStatus } from '../api/client'

export default function StatusBar({ sessionId }) {
  const [backendUp, setBackendUp] = useState(false)
  const [indexInfo, setIndexInfo] = useState(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const check = async () => {
      try {
        await checkHealth()
        setBackendUp(true)
        if (sessionId) {
          const statusRes = await checkStatus(sessionId)
          setIndexInfo(statusRes.data)
        }
      } catch {
        setBackendUp(false)
      } finally {
        setChecking(false)
      }
    }
    check()
  }, [sessionId])

  if (checking) {
    return (
      <div className="flex items-center gap-2 text-xs px-3 py-2 rounded-md bg-gray-100 text-gray-500">
        Checking backend...
      </div>
    )
  }

  return (
    <div
      className={`flex items-center gap-2 text-xs px-3 py-2 rounded-md ${
        backendUp
          ? 'bg-green-50 text-green-800'
          : 'bg-red-50 text-red-800'
      }`}
    >
      <span
        className={`w-2 h-2 rounded-full ${
          backendUp ? 'bg-green-600' : 'bg-red-600'
        }`}
      />
      {backendUp ? 'Backend connected' : 'Backend not connected'}

    </div>
  )
}