/**
 * Base API Client Configuration
 * Axios instance with interceptors and error handling
 */
import axios, { type AxiosInstance, type AxiosError } from 'axios'

// Base URL from environment or empty string to use Vite proxy
const BASE_URL = import.meta.env.VITE_API_URL || ''

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.params = {
      ...config.params,
      _t: Date.now(),
    }

    console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error: AxiosError) => {
    console.error('❌ Response Error:', error.response?.status, error.message)

    // Handle specific error codes
    if (error.response) {
      switch (error.response.status) {
        case 404:
          console.error('Resource not found')
          break
        case 500:
          console.error('Server error')
          break
        case 400:
          console.error('Bad request:', error.response.data)
          break
      }
    } else if (error.request) {
      console.error('No response received from server')
    } else {
      console.error('Error setting up request:', error.message)
    }

    return Promise.reject(error)
  }
)

export default apiClient
