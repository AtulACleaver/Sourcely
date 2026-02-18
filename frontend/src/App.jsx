import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [status, setStatus] = useState('checking...')

  useEffect(() => {
    axios.get('http://localhost:8000/health')
      .then(res => setStatus(res.data.message))
      .catch(err => setStatus('Backend not connected'))
  }, [])

  return <h1>Backend status: {status}</h1>
}

export default App