import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import axios from 'axios'
import App from './App.jsx'
import './index.css'

// Production'da console.log'ları devre dışı bırak (güvenlik)
if (import.meta.env.PROD) {
  console.log = () => {}
  console.error = () => {}
  console.warn = () => {}
  console.info = () => {}
  console.debug = () => {}
}

axios.defaults.withCredentials = true

// Request interceptor - Authorization header ekle
axios.interceptors.request.use(
  (config) => {
    // localStorage'dan token al ve Authorization header'a ekle
    const accessToken = localStorage.getItem('access_token')
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - 401 hatalarını yönet ve token yenile
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // 401 hatası ve henüz retry yapılmamışsa
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Refresh token ile yenileme dene
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const API_URL = import.meta.env.VITE_API_URL || '/api'
          const response = await axios.post(`${API_URL}/refresh`, {}, {
            headers: {
              'Authorization': `Bearer ${refreshToken}`
            }
          })
          
          // Yeni token'ları kaydet
          if (response.data.access_token) {
            localStorage.setItem('access_token', response.data.access_token)
          }
          if (response.data.refresh_token) {
            localStorage.setItem('refresh_token', response.data.refresh_token)
          }
          
          // Orijinal isteği yeni token ile tekrar dene
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
          return axios(originalRequest)
        } catch (refreshError) {
          // Refresh başarısız - token'ları temizle ve login'e yönlendir
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          // Sessizce reddet (kullanıcı login sayfasına yönlendirilecek)
          return Promise.reject(refreshError)
        }
      }
    }
    
    // Production'da hataları konsola yazdırma (güvenlik)
    // Development modunda hata göster
    if (import.meta.env.DEV && error.response?.status !== 401) {
      console.error('API Error:', error)
    }
    return Promise.reject(error)
  }
)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
