import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import Logo from './Logo'

const API_URL = import.meta.env.VITE_API_URL || '/api';

function Sidebar() {
  const location = useLocation();
  const [isAdmin, setIsAdmin] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkUser();
  }, [location.pathname]); // Sayfa değiştiğinde kullanıcı durumunu kontrol et

  const checkUser = async () => {
    try {
      const res = await axios.get(`${API_URL}/users/me`);
      setUser(res.data);
      if (res.data.is_superuser) {
        setIsAdmin(true);
      }
    } catch (err) {
      // Kullanıcı giriş yapmamış
      setUser(null);
      setIsAdmin(false);
    }
  };

  const menuItems = [
    { path: '/', label: 'Anasayfa', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  ];

  if (isAdmin) {
    menuItems.push({
      path: '/admin/hata-raporlari',
      label: 'Hata Raporları',
      icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
    });
  }

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 flex flex-col shadow-sm">
      {/* Başlık */}
      <div className="p-6 border-b border-gray-200">
        <Link to="/" className="block">
          <Logo size="sm" showText={true} />
        </Link>
      </div>

      {/* Menü */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
              isActive(item.path)
                ? 'bg-blue-50 text-blue-700 border border-blue-200'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <svg
              className="w-5 h-5 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d={item.icon}
              />
            </svg>
            {item.label}
          </Link>
        ))}
      </nav>

      {/* Kullanıcı Bölümü */}
      <div className="p-4 border-t border-gray-200">
        {user ? (
          <div className="flex items-center px-4 py-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
            </div>
            <div className="ml-3 flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user.full_name}</p>
              <p className="text-xs text-gray-500 truncate">{user.email}</p>
            </div>
          </div>
        ) : (
          <Link to="/giris" className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
            Giriş Yap
          </Link>
        )}
      </div>
    </div>
  );
}

export default Sidebar;



