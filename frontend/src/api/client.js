import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    console.error(`[API] ${status ?? 'réseau'} — ${detail ?? error.message}`)
    return Promise.reject(error)
  },
)

export default client
