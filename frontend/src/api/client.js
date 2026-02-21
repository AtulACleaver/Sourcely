import axios from 'axios'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

export const checkHealth = () => API.get('/health')

export const checkStatus = (sessionId) =>
  API.get('/status', { params: sessionId ? { session_id: sessionId } : {} })

export const createSession = () => API.post('/session')

export const uploadPDF = (file, sessionId) => {
  const formData = new FormData()
  formData.append('file', file)
  return API.post(`/upload?session_id=${sessionId}`, formData)
}

export const askQuestion = (question, sessionId, k = 5) =>
  API.post('/query', null, { params: { question, session_id: sessionId, k } })

export default API
