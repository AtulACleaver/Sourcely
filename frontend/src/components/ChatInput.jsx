// src/components/ChatInput.jsx

import { useState } from 'react'

export default function ChatInput({ onAsk, disabled }) {
  const [question, setQuestion] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = question.trim()
    if (!trimmed) return
    onAsk(trimmed)
    setQuestion('')
  }

  return (
    <form className="flex gap-2" onSubmit={handleSubmit}>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder={
          disabled
            ? 'Upload a PDF first...'
            : 'Ask a question about your document...'
        }
        disabled={disabled}
        className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg text-sm
          outline-none transition-colors duration-200
          focus:border-indigo-500
          disabled:bg-gray-100 disabled:cursor-not-allowed"
      />
      <button
        type="submit"
        disabled={disabled || !question.trim()}
        className="px-6 py-3 bg-indigo-600 text-white rounded-lg text-sm font-semibold
          transition-colors duration-200
          hover:bg-indigo-700
          disabled:bg-indigo-300 disabled:cursor-not-allowed"
      >
        Ask
      </button>
    </form>
  )
}