// src/api/client.js

import axios from 'axios'

// Create a reusable axios instance with the backend URL
// If VITE_API_URL is set (for production), use that. Otherwise, localhost.
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})


/**
 * Check if the backend is running.
 * GET /health -> { message: "Sourcely is running!!" }
 */
export const checkHealth = () => API.get('/health')


/**
 * Check if a FAISS index exists and how many chunks it has.
 * GET /status -> { index_loaded: true/false, num_chunks: number }
 */
export const checkStatus = () => API.get('/status')


/**
 * Upload a PDF file to the backend.
 * POST /upload (multipart form data)
 *
 * Why FormData? Browser file uploads use multipart encoding, not JSON.
 * FormData handles this automatically. You MUST use the key 'file'
 * because that's what FastAPI's UploadFile parameter expects.
 *
 * @param {File} file - The PDF file object from an <input type="file">
 * @returns { filename, status, num_pages, num_chunks }
 */
export const uploadPDF = (file) => {
  const formData = new FormData()
  formData.append('file', file)  // 'file' matches FastAPI's parameter name
  return API.post('/upload', formData)
  // NOTE: Do NOT set Content-Type header manually.
  // Axios + FormData sets it to multipart/form-data with the correct boundary.
  // If you set it yourself, the boundary will be wrong and the upload will fail.
}


/**
 * Ask a question about the uploaded document.
 * POST /query?question=...&k=5
 *
 * Why params instead of body? Because your FastAPI endpoint uses
 * query parameters (question: str, k: int), not a JSON body.
 * Axios puts 'params' into the URL as ?question=...&k=5
 *
 * @param {string} question - The user's question
 * @param {number} k - Number of chunks to retrieve (default 5)
 * @returns { question, answer, citations, retrieved_chunks }
 */
export const askQuestion = (question, k = 5) =>
  API.post('/query', null, { params: { question, k } })


export default API