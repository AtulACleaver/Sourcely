import { useState } from 'react'
import StatusBar from './components/StatusBar'
import FileUpload from './components/FileUpload'
import ChatInput from './components/ChatInput'
import AnswerDisplay from './components/AnswerDisplay'
import { askQuestion } from './api/client'

export default function App() {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [answer, setAnswer] = useState(null)
  const [citations, setCitations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleUploadSuccess = (data) => {
    // reset state on new upload
    setUploadedFile(data)
    setAnswer(null)
    setCitations([])
    setError('')
  }

  const handleAsk = async (question) => {
    // call backend query endpoint
    setLoading(true)
    setError('')
    setAnswer(null)
    setCitations([])

    try {
      const res = await askQuestion(question)
      setAnswer(res.data.answer)
      setCitations(res.data.citations)
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Something went wrong'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-5 py-5 min-h-screen">
      <StatusBar />

      <header className="text-center pt-10 pb-5">
        <h1 className="text-3xl font-bold text-gray-900">Sourcely</h1>
        <p className="text-gray-500 text-sm mt-1">
          Ask questions about your PDFs. Get answers with citations.
        </p>
      </header>

      <main className="flex flex-col gap-5 pt-5">
        <FileUpload onUploadSuccess={handleUploadSuccess} />

        {uploadedFile && (
          <p className="text-sm text-gray-600 text-center">
            📄 <strong>{uploadedFile.filename}</strong> ready
            ({uploadedFile.num_chunks} chunks)
          </p>
        )}

        <ChatInput
          onAsk={handleAsk}
          disabled={!uploadedFile || loading}
        />

        {error && (
          <p className="text-sm text-red-800 bg-red-50 px-4 py-2.5 rounded-md text-center">
            {error}
          </p>
        )}

        <AnswerDisplay
          answer={answer}
          citations={citations}
          loading={loading}
        />
      </main>
    </div>
  )
}