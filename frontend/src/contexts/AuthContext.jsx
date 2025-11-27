import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);

  // JWT token'ı decode ederek expire zamanını kontrol et
  const isTokenValid = useCallback(() => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      return false;
    }
    
    try {
      // JWT token'ı decode et (base64)
      const payload = JSON.parse(atob(accessToken.split('.')[1]));
      const exp = payload.exp;
      if (!exp) {
        return false;
      }
      
      // Token expire olmuş mu? (30 saniye buffer ekle)
      const now = Math.floor(Date.now() / 1000);
      return exp > (now + 30);
    } catch (err) {
      // Token decode edilemezse geçersiz say
      return false;
    }
  }, []);

  // Refresh token'ın geçerliliğini kontrol et
  const isRefreshTokenValid = useCallback(() => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return false;
    }
    
    try {
      // JWT token'ı decode et (base64)
      const payload = JSON.parse(atob(refreshToken.split('.')[1]));
      const exp = payload.exp;
      const tokenType = payload.type;
      
      if (!exp || tokenType !== 'refresh') {
        return false;
      }
      
      // Token expire olmuş mu?
      const now = Math.floor(Date.now() / 1000);
      return exp > now;
    } catch (err) {
      // Token decode edilemezse geçersiz say
      return false;
    }
  }, []);

  const checkAuth = useCallback(async () => {
    // Access token yoksa veya geçersizse
    if (!isTokenValid()) {
      // Refresh token da geçersizse direkt çık
      if (!isRefreshTokenValid()) {
        setIsLoggedIn(false);
        setUser(null);
        setAuthChecked(true);
        return;
      }
      // Refresh token geçerliyse, axios interceptor refresh yapacak
      // Bu durumda sadece durumu güncelle ve bekle
      setIsLoggedIn(false);
      setUser(null);
      setAuthChecked(true);
      return;
    }

    // Access token geçerliyse profil bilgisini al
    const fetchProfile = async () => {
      try {
        const res = await axios.get(`${API_URL}/users/me`);
        setUser(res.data);
        setIsLoggedIn(true);
        setAuthChecked(true);
      } catch (err) {
        // 401 hatası - axios interceptor zaten refresh deneyecek
        if (err.response?.status === 401) {
          setIsLoggedIn(false);
          setUser(null);
          setAuthChecked(true);
        }
      }
    };

    await fetchProfile();
  }, [isTokenValid, isRefreshTokenValid]);

  // Sadece ilk yüklemede kontrol et
  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken && isTokenValid()) {
      checkAuth();
    } else {
      // Token yoksa veya geçersizse direkt misafir kullanıcı olarak işaretle
      setIsLoggedIn(false);
      setUser(null);
      setAuthChecked(true);
    }
  }, []); // Sadece mount'ta çalışır

  // Token değiştiğinde kontrol et (login/logout sonrası)
  useEffect(() => {
    const handleStorageChange = () => {
      if (!isTokenValid()) {
        setIsLoggedIn(false);
        setUser(null);
        setAuthChecked(false);
      } else if (!authChecked) {
        checkAuth();
      }
    };
    
    // Custom event listener (aynı tab'da localStorage değişiklikleri için)
    const handleAuthChange = () => {
      if (isTokenValid()) {
        checkAuth();
      } else {
        setIsLoggedIn(false);
        setUser(null);
        setAuthChecked(false);
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth-changed', handleAuthChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-changed', handleAuthChange);
    };
  }, [authChecked, isTokenValid, checkAuth]);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsLoggedIn(false);
    setUser(null);
    setAuthChecked(false);
    // Auth değişikliğini bildir
    window.dispatchEvent(new Event('auth-changed'));
  }, []);

  const value = {
    isLoggedIn,
    user,
    authChecked,
    checkAuth,
    logout,
    isAuthenticated: isLoggedIn && authChecked,
    isAdmin: user?.is_superuser || false
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

