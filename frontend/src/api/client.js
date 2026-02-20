import axios from 'axios'

const API = axios.create({
  baseURL: 'http://localhost:8000'
})

export const checkHealth = () => API.get('/health')
export const uploadPDF = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return API.post('/upload', formData)
}
export const askQuestion = (question) =>
  API.post('/query', null, { params: { question } })

export default API