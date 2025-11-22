import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_URL = '/api';

function Layout({ children }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const res = await axios.get(`${API_URL}/users/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(res.data);
        setIsLoggedIn(true);
      } catch (err) {
        console.error('Auth check failed:', err);
        localStorage.removeItem('token');
        setIsLoggedIn(false);
        setUser(null);
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setUser(null);
    setIsUserMenuOpen(false);
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Üst Menü */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            {/* Logo ve Ana Menü */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <span className="text-lg font-semibold text-gray-900">Konkordato Takip</span>
              </Link>
              
              {/* Desktop Menü */}
              <div className="hidden md:flex md:ml-8 md:space-x-4">
                <Link
                  to="/"
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    location.pathname === '/'
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  İlanlar
                </Link>
              </div>
            </div>

            {/* Sağ Taraf - Kullanıcı Menüsü */}
            <div className="flex items-center space-x-4">
              {isLoggedIn ? (
                <div className="relative">
                  <button
                    onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                    className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900 focus:outline-none"
                  >
                    <span>{user?.full_name || 'Kullanıcı'}</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {isUserMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 border border-gray-200">
                      <Link
                        to="/profil"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        Profil
                      </Link>
                      <hr className="my-1 border-gray-200" />
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Çıkış Yap
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Link
                    to="/giris"
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 rounded-md transition-colors"
                  >
                    Giriş Yap
                  </Link>
                  <Link
                    to="/kayit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                  >
                    Kayıt Ol
                  </Link>
                </div>
              )}

              {/* Mobil Menü Butonu */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-50"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {isMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {/* Mobil Menü */}
          {isMenuOpen && (
            <div className="md:hidden border-t border-gray-200 py-2">
              <Link
                to="/"
                className={`block px-4 py-2 text-sm font-medium rounded-md ${
                  location.pathname === '/'
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                İlanlar
              </Link>
              {!isLoggedIn && (
                <>
                  <Link
                    to="/giris"
                    className="block px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Giriş Yap
                  </Link>
                  <Link
                    to="/kayit"
                    className="block px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Kayıt Ol
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
      </nav>

      {/* Ana İçerik */}
      <main>{children}</main>
    </div>
  )
}

export default Layout
