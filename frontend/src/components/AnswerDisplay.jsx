// src/components/AnswerDisplay.jsx

export default function AnswerDisplay({ answer, citations, loading }) {
  if (loading) {
    return (
      <div className="flex flex-col items-center gap-2 py-8 text-gray-500">
        <div className="w-6 h-6 border-3 border-gray-200 border-t-indigo-500 rounded-full animate-spin" />
        <p className="text-sm">Searching document and generating answer...</p>
      </div>
    )
  }

  if (!answer) return null

  return (
    <div className="flex flex-col gap-4">
      {/* Answer box */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h3 className="text-xs uppercase tracking-wide text-gray-400 mb-2">
          Answer
        </h3>
        <p className="text-base leading-7 text-gray-900">{answer}</p>
      </div>

      {/* Citations */}
      {citations.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h4 className="text-xs uppercase tracking-wide text-gray-400 mb-3">
            Sources ({citations.length})
          </h4>
          <div className="flex flex-col gap-2.5">
            {citations.map((citation, index) => (
              <div
                key={index}
                className="bg-gray-50 border border-gray-100 rounded-lg p-3
                  transition-colors duration-200 hover:border-indigo-200"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded">
                    Chunk {citation.chunk_id}
                  </span>
                  <span className="text-xs text-gray-400">
                    Page {citation.page_number}
                  </span>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {citation.excerpt}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}