/**
 * Base API Client Configuration
 * Axios instance with interceptors and error handling
 */
import axios, { type AxiosInstance, type AxiosError } from 'axios'

// Base URL from environment or empty string to use Vite proxy
const BASE_URL = import.meta.env.VITE_API_URL || ''

// Create axios instance
const axiosInstance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
axiosInstance.interceptors.request.use(
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
axiosInstance.interceptors.response.use(
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

// Helper methods with type inference
export const apiClient = {
  async get<T>(url: string, config?: any): Promise<T> {
    const response = await axiosInstance.get<T>(url, config)
    return response.data
  },

  async post<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await axiosInstance.post<T>(url, data, config)
    return response.data
  },

  async patch<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await axiosInstance.patch<T>(url, data, config)
    return response.data
  },

  async put<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await axiosInstance.put<T>(url, data, config)
    return response.data
  },

  async delete<T = void>(url: string, config?: any): Promise<T> {
    const response = await axiosInstance.delete<T>(url, config)
    return response.data
  }
}

// Export raw axios instance for advanced use cases
export const axiosClient = axiosInstance

export default axiosInstance
