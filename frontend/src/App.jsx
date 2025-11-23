import { Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import Layout from './components/Layout'
import IlanList from './pages/IlanList'
import IlanDetay from './pages/IlanDetay'
import Register from './pages/Register'
import Login from './pages/Login'

// Admin sayfasını Lazy Load yap (Code Splitting & Security)
// Normal kullanıcılar bu sayfanın kodlarını (JS bundle) hiç indirmezler.
// Bu sayede sayfanın içeriği ve yapısı kaynak kodlarında görünmez.
const AdminHataRaporlari = lazy(() => import('./pages/AdminHataRaporlari'));

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<IlanList />} />
        <Route path="/ilan/:id" element={<IlanDetay />} />
        <Route path="/kayit" element={<Register />} />
        <Route path="/giris" element={<Login />} />
        <Route 
          path="/admin/hata-raporlari" 
          element={
            <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Yükleniyor...</div>}>
              <AdminHataRaporlari />
            </Suspense>
          } 
        />
      </Routes>
    </Layout>
  )
}

export default App
