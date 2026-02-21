// src/components/FileUpload.jsx

import { useState } from 'react'
import { uploadPDF } from '../api/client'

export default function FileUpload({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [dragOver, setDragOver] = useState(false)

  const handleFile = async (file) => {
    if (!file) return

    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files are accepted.')
      setMessage('')
      return
    }

    setError('')
    setMessage('')
    setUploading(true)

    try {
      const res = await uploadPDF(file)
      setMessage(
        `${res.data.filename} - ${res.data.num_pages} pages, ${res.data.num_chunks} chunks indexed`
      )
      onUploadSuccess(res.data)
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Upload failed'
      setError(detail)
    } finally {
      setUploading(false)
    }
  }

  const handleInputChange = (e) => handleFile(e.target.files[0])

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => setDragOver(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <div
      className={`
        relative border-2 border-dashed rounded-xl p-8 text-center
        transition-all duration-200
        ${dragOver
          ? 'border-indigo-500 bg-indigo-50'
          : uploading
            ? 'border-indigo-500 border-solid'
            : 'border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50'
        }
        ${uploading ? 'cursor-default' : 'cursor-pointer'}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {uploading ? (
        <div className="flex flex-col items-center gap-2">
          <div className="w-6 h-6 border-3 border-gray-200 border-t-indigo-500 rounded-full animate-spin" />
          <p className="text-gray-700 text-sm">Processing PDF... extracting, chunking, embedding</p>
          <p className="text-xs text-gray-400">This can take 30-60 seconds depending on the file size.</p>
        </div>
      ) : (
        <>
          <p className="text-3xl mb-2">📄</p>
          <p className="text-gray-500 text-sm">Drop a PDF here or click to browse</p>
          <input
            type="file"
            accept=".pdf"
            onChange={handleInputChange}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
        </>
      )}

      {message && (
        <p className="mt-3 text-sm text-green-800 bg-green-50 px-3 py-2 rounded-md">
          {message}
        </p>
      )}
      {error && (
        <p className="mt-3 text-sm text-red-800 bg-red-50 px-3 py-2 rounded-md">
          {error}
        </p>
      )}
    </div>
  )
}