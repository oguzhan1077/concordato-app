import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'
const NAME_REGEX = /^[A-Za-zÇĞİÖŞÜçğöşıü0-9\s.'-]{2,100}$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,128}$/

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm_password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Sayfa açıldığında scroll pozisyonunu en üste al
    window.scrollTo(0, 0);
  }, []);

  const validate = () => {
    const newErrors = {}
    const name = formData.full_name.trim()
    const email = formData.email.trim().toLowerCase()
    const password = formData.password

    if (!name) {
      newErrors.full_name = 'Ad Soyad gereklidir'
    } else if (!NAME_REGEX.test(name)) {
      newErrors.full_name = 'Ad alanı sadece harf, rakam, boşluk ve .\'- karakterleri içerebilir'
    }

    if (!email) {
      newErrors.email = 'E-posta gereklidir'
    } else if (email.length > 254 || !EMAIL_REGEX.test(email)) {
      newErrors.email = 'Geçerli bir e-posta adresi giriniz (254 karakter sınırı)'
    }

    if (!PASSWORD_REGEX.test(password)) {
      newErrors.password = 'Şifre 8-128 karakter olmalı ve büyük, küçük harf, rakam ve özel karakter içermeli'
    }

    if (password !== formData.confirm_password) {
      newErrors.confirm_password = 'Şifreler eşleşmiyor'
    }
    return newErrors
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const response = await axios.post(`${API_URL}/register`, {
        full_name: formData.full_name.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password
      })
      
      // Backend her zaman generic mesaj döner (güvenlik için)
      // Email zaten kayıtlı olsa bile kullanıcı bunu bilemez
      navigate('/giris', { 
        state: { 
          message: response.data.message || 'Kayıt işleminiz alındı. E-posta adresinizi kontrol ediniz.' 
        } 
      });
    } catch (err) {
      // Sadece rate limit veya sunucu hatalarında buraya düşer
      setErrors({ 
        submit: 'Kayıt sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyiniz.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Hata varsa temizle
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 transition-colors">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          Hesap Oluştur
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Zaten hesabınız var mı?{' '}
          <Link to="/giris" className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300">
            Giriş Yap
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {errors.submit && (
            <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded text-sm">
              {errors.submit}
            </div>
          )}
          
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Ad Soyad
              </label>
              <div className="mt-1">
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  autoComplete="name"
                  required
                  maxLength={100}
                  value={formData.full_name}
                  onChange={handleChange}
                  className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:text-white ${
                    errors.full_name ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                  }`}
                  pattern={NAME_REGEX.source}
                  title="2-100 karakter. Harf, rakam, boşluk, . ' - karakterlerine izin verilir"
                />
                {errors.full_name && (
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.full_name}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                E-posta adresi
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  maxLength={254}
                  value={formData.email}
                  onChange={handleChange}
                  className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:text-white ${
                    errors.email ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                  }`}
                  pattern={EMAIL_REGEX.source}
                  title="Geçerli bir e-posta adresi giriniz"
                />
                {errors.email && (
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.email}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Şifre
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  minLength={8}
                  maxLength={128}
                  value={formData.password}
                  onChange={handleChange}
                  className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:text-white ${
                    errors.password ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                  }`}
                  title="8-128 karakter, büyük/küçük harf, sayı ve özel karakter içermelidir"
                />
                {errors.password && (
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.password}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Şifre Tekrar
              </label>
              <div className="mt-1">
                <input
                  id="confirm_password"
                  name="confirm_password"
                  type="password"
                  autoComplete="new-password"
                  required
                  minLength={8}
                  maxLength={128}
                  value={formData.confirm_password}
                  onChange={handleChange}
                  className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:text-white ${
                    errors.confirm_password ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                  }`}
                  title="Şifre tekrarınızı giriniz"
                />
                {errors.confirm_password && (
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.confirm_password}</p>
                )}
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:ring-offset-gray-800 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Kaydediliyor...' : 'Kayıt Ol'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Register;

