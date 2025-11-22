import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import IlanList from './pages/IlanList'
import IlanDetay from './pages/IlanDetay'
import Register from './pages/Register'
import Login from './pages/Login'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<IlanList />} />
        <Route path="/ilan/:id" element={<IlanDetay />} />
        <Route path="/kayit" element={<Register />} />
        <Route path="/giris" element={<Login />} />
      </Routes>
    </Layout>
  )
}

export default App
