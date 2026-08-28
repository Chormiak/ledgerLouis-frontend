
import axios from 'axios'
import { useUserStore } from '@/stores/userStore'


const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  timeout: 10000,                
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    const token = userStore.accessToken

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      const requestToken = error.config?.headers?.Authorization?.replace('Bearer ', '')

      // Uma resposta atrasada da sessão anterior não pode apagar o token novo.
      if (requestToken && requestToken === userStore.accessToken) {
        userStore.clearTokens()
      }
    }

    if (error.response?.status === 500) {
      console.error('Erro interno no servidor')
    }

    return Promise.reject(error)
  }
)

export default api