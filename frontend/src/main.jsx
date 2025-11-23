import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import axios from 'axios'
import App from './App.jsx'
import './index.css'

axios.defaults.withCredentials = true

// Axios interceptor - 401 hatalarını sessizce yönet
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 hatalarını konsola yazdırma (giriş yapılmamış kullanıcı normal bir durum)
    if (error.response?.status === 401) {
      // Sessizce reddet, konsola yazma
      return Promise.reject(error);
    }
    // Diğer hataları normal şekilde logla
    if (error.response?.status !== 401) {
      console.error('API Error:', error);
    }
    return Promise.reject(error);
  }
);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
