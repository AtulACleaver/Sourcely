// src/api/client.js

import axios from 'axios'

// backend api instance
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})


// check if the backend is running
export const checkHealth = () => API.get('/health')


// check the index status
export const checkStatus = () => API.get('/status')


// upload a pdf file
export const uploadPDF = (file) => {
  const formData = new FormData()
  formData.append('file', file)  // 'file' matches FastAPI's parameter name
  return API.post('/upload', formData)
}


// ask a question about the document
export const askQuestion = (question, k = 5) =>
  API.post('/query', null, { params: { question, k } })


export default API