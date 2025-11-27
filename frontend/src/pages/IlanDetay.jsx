import { useState, useEffect, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api';

function IlanDetay() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ilan, setIlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportForm, setReportForm] = useState({
    kategori: 'yanlis_bilgi',
    aciklama: ''
  });
  const [reportError, setReportError] = useState('');
  const [reportSuccess, setReportSuccess] = useState('');
  const [reportLoading, setReportLoading] = useState(false);
  const [userReport, setUserReport] = useState(null);
  const [reportStatusLoading, setReportStatusLoading] = useState(false);

  const checkReportStatus = useCallback(async () => {
    // id kontrolü
    if (!id || isNaN(parseInt(id))) {
      return;
    }
    
    setReportStatusLoading(true);
    try {
      const res = await axios.get(`${API_URL}/ilan/${id}/rapor-durumu`);
      if (res.data && res.data.has_report) {
        setUserReport(res.data.rapor);
      } else {
        setUserReport(null);
      }
    } catch (err) {
      // 401 hatası normal (giriş yapılmamış veya token geçersiz)
      // 404 hatası normal (rapor yok)
      if (err.response?.status !== 401 && err.response?.status !== 404) {
        // Beklenmeyen hatalar için sadece development'ta log
        if (import.meta.env.DEV) {
          console.log('Rapor durumu kontrol edilemedi:', err);
        }
      }
      setUserReport(null);
    } finally {
      setReportStatusLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Sayfa açıldığında scroll pozisyonunu en üste al
    window.scrollTo(0, 0);
    
    // id parametresi yoksa veya geçersizse işlem yapma
    if (!id || isNaN(parseInt(id))) {
      setError("Geçersiz ilan ID'si");
      setLoading(false);
      return;
    }
    
    fetchIlanDetay();
    checkAuth();
  }, [id]);

  const checkAuth = async () => {
    try {
      await axios.get(`${API_URL}/users/me`);
      setIsAuthenticated(true);
    } catch (err) {
      setIsAuthenticated(false);
      setUserReport(null);
      // 401 hatası normal bir durum (giriş yapılmamış), sessizce geç
    }
  };

  // Kullanıcı giriş yapmışsa ve id geçerliyse, rapor durumunu kontrol et
  useEffect(() => {
    if (isAuthenticated && id && !isNaN(parseInt(id))) {
      checkReportStatus();
    } else {
      setUserReport(null);
    }
  }, [isAuthenticated, id, checkReportStatus]);

  const fetchIlanDetay = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_URL}/ilanlar/${id}`);
      setIlan(res.data);
    } catch (err) {
      if (import.meta.env.DEV) {
        console.error("İlan detay hatası:", err);
      }
      setError("İlan bulunamadı");
    } finally {
      setLoading(false);
    }
  };

  const handleReportClick = () => {
    setShowReportModal(true);
    setReportError('');
    setReportSuccess('');
  };

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    setReportError('');
    setReportSuccess('');

    if (reportForm.aciklama.trim().length < 10) {
      setReportError('Açıklama en az 10 karakter olmalıdır');
      return;
    }

    if (reportForm.aciklama.trim().length > 1000) {
      setReportError('Açıklama en fazla 1000 karakter olmalıdır');
      return;
    }

    setReportLoading(true);

    try {
      await axios.post(`${API_URL}/rapor-olustur`, {
        ilan_id: parseInt(id),
        kategori: reportForm.kategori,
        aciklama: reportForm.aciklama.trim()
      });

      setReportSuccess('Raporunuz başarıyla gönderildi. Teşekkür ederiz!');
      setReportForm({ kategori: 'yanlis_bilgi', aciklama: '' });
      
      // Rapor durumunu yeniden kontrol et
      await checkReportStatus();
      
      setTimeout(() => {
        setShowReportModal(false);
        setReportSuccess('');
      }, 2000);
    } catch (err) {
      if (import.meta.env.DEV) {
        console.error('Rapor gönderme hatası:', err);
      }
      setReportError(err.response?.data?.detail || 'Rapor gönderilemedi. Lütfen tekrar deneyin.');
    } finally {
      setReportLoading(false);
    }
  };

  const handleReportChange = (e) => {
    setReportForm({
      ...reportForm,
      [e.target.name]: e.target.value
    });
    if (reportError) setReportError('');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 transition-colors">
        <div className="max-w-5xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-12 text-center">
            <div className="flex items-center justify-center">
              <svg className="animate-spin h-8 w-8 mr-3 text-blue-600 dark:text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-gray-700 dark:text-gray-300 text-lg">Yükleniyor...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !ilan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 transition-colors">
        <div className="max-w-5xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-12 text-center">
            <svg className="h-16 w-16 text-red-400 dark:text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p className="text-red-600 dark:text-red-400 mb-6 text-lg font-medium">{error || "İlan bulunamadı"}</p>
            <Link to="/" className="inline-flex items-center px-6 py-3 bg-blue-600 dark:bg-blue-700 text-white font-medium rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800 transition-all shadow-sm hover:shadow-md">
              ← Ana Sayfaya Dön
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Mahkeme ve dosya esas no bilgisini borçlulardan al (genelde ilk borçluda)
  const mahkemeAdi = ilan.borclular?.[0]?.mahkeme_adi || '-';
  const dosyaEsasNo = ilan.borclular?.[0]?.dosya_esas_no || '-';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 transition-colors">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link 
            to="/" 
            className="inline-flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 mb-4 transition-colors font-medium"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Ana Sayfaya Dön
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">İlan Detayları</h1>
          <p className="text-gray-600 dark:text-gray-400">İlan numarası: <span className="font-semibold text-gray-900 dark:text-white">{ilan.ilan_no}</span></p>
        </div>

        {/* İlan Başlık Kartı */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{ilan.baslik || 'Başlık Yok'}</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Temel Bilgiler */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Temel Bilgiler
            </h3>
            <dl className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <dt className="text-sm text-gray-600 dark:text-gray-400 mb-1">Yayın Tarihi</dt>
                <dd className="text-base font-semibold text-gray-900 dark:text-white">{ilan.yayin_tarihi || '-'}</dd>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <dt className="text-sm text-gray-600 dark:text-gray-400 mb-1">İlan Türü</dt>
                <dd className="text-base font-semibold text-gray-900 dark:text-white">{ilan.ilan_turu || '-'}</dd>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <dt className="text-sm text-gray-600 dark:text-gray-400 mb-1">Şehir</dt>
                <dd className="text-base font-semibold text-gray-900 dark:text-white">{ilan.sehir || '-'}</dd>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <dt className="text-sm text-gray-600 dark:text-gray-400 mb-1">İlçe</dt>
                <dd className="text-base font-semibold text-gray-900 dark:text-white">{ilan.ilce || '-'}</dd>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <dt className="text-sm text-gray-600 dark:text-gray-400 mb-1">Mahkeme</dt>
                <dd className="text-base font-semibold text-gray-900 dark:text-white">{mahkemeAdi}</dd>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <dt className="text-sm text-gray-600 dark:text-gray-400 mb-1">Dosya Esas No</dt>
                <dd className="text-base font-semibold text-gray-900 dark:text-white">{dosyaEsasNo}</dd>
              </div>
            </dl>
          </div>

          {/* İşlemler */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              İşlemler
            </h3>
            <div className="space-y-3">
              {ilan.link ? (
                <a 
                  href={ilan.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center justify-center px-4 py-3 bg-blue-600 dark:bg-blue-700 text-white text-sm font-medium rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800 transition-all shadow-sm hover:shadow-md"
                >
                  Orijinal İlanı Görüntüle
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center">Link mevcut değil</p>
              )}
              
              {isAuthenticated && (
                <>
                  {userReport && (userReport.durum === 'beklemede' || userReport.durum === 'inceleniyor') ? (
                    // Beklemede veya İnceleniyor - Durum göster, yeni rapor vermesine izin verme
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                      <div className="flex items-start">
                        <svg className="w-5 h-5 mr-2 mt-0.5 text-blue-600 dark:text-blue-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-1">
                            Hata Bildirildi
                          </p>
                          <p className="text-xs text-blue-700 dark:text-blue-300 mb-2">
                            Kategori: {userReport.kategori.replace('_', ' ').toUpperCase()}
                          </p>
                          <div className="flex items-center mb-2">
                            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium mr-2">Durum:</span>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                              userReport.durum === 'beklemede' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                              'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                            }`}>
                              {userReport.durum === 'beklemede' ? 'Beklemede' : 'İnceleniyor'}
                            </span>
                          </div>
                          <p className="text-xs text-blue-600 dark:text-blue-400">
                            Tarih: {new Date(userReport.olusturma_tarihi).toLocaleDateString('tr-TR')}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 italic">
                            Raporunuz inceleniyor. İşlem tamamlandığında buradan görebilirsiniz.
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : userReport && (userReport.durum === 'cozuldu' || userReport.durum === 'reddedildi') ? (
                    // Çözüldü veya Reddedildi - Durum göster ve yeni rapor verme seçeneği sun
                    <div className="space-y-3">
                      <div className={`border rounded-lg p-4 ${
                        userReport.durum === 'cozuldu' 
                          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
                          : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                      }`}>
                        <div className="flex items-start">
                          <svg className={`w-5 h-5 mr-2 mt-0.5 flex-shrink-0 ${
                            userReport.durum === 'cozuldu' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div className="flex-1">
                            <p className={`text-sm font-semibold mb-1 ${
                              userReport.durum === 'cozuldu' ? 'text-green-900 dark:text-green-200' : 'text-red-900 dark:text-red-200'
                            }`}>
                              Önceki Rapor: {userReport.durum === 'cozuldu' ? 'Çözüldü' : 'Reddedildi'}
                            </p>
                            <p className={`text-xs mb-2 ${
                              userReport.durum === 'cozuldu' ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
                            }`}>
                              Kategori: {userReport.kategori.replace('_', ' ').toUpperCase()}
                            </p>
                            <p className={`text-xs ${
                              userReport.durum === 'cozuldu' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                            }`}>
                              Tarih: {new Date(userReport.olusturma_tarihi).toLocaleDateString('tr-TR')}
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={handleReportClick}
                        className="flex items-center justify-center w-full px-4 py-3 bg-orange-500 dark:bg-orange-600 text-white text-sm font-medium rounded-lg hover:bg-orange-600 dark:hover:bg-orange-700 transition-all shadow-sm hover:shadow-md"
                      >
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        Yeni Hata Bildir
                      </button>
                      <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                        Farklı bir sorun mu gördünüz? Tekrar bildirebilirsiniz.
                      </p>
                    </div>
                  ) : (
                    // Hiç rapor verilmemiş - Normal hata bildir butonu
                    <>
                      <button
                        onClick={handleReportClick}
                        className="flex items-center justify-center w-full px-4 py-3 bg-red-500 dark:bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-600 dark:hover:bg-red-700 transition-all shadow-sm hover:shadow-md"
                      >
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        Hata Bildir
                      </button>
                      <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                        İlanda hata gördüyseniz bildirebilirsiniz
                      </p>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* Borçlu Bilgileri */}
        {ilan.borclular && ilan.borclular.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Borçlu Bilgileri ({ilan.borclular.length})
            </h3>
            <div className="space-y-4">
              {ilan.borclular.map((borclu, index) => (
                <div key={borclu.id || index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-5 hover:border-blue-300 dark:hover:border-blue-600 transition-colors bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-700">
                  <div className="flex items-start justify-between mb-4">
                    <h4 className="text-lg font-bold text-gray-900 dark:text-white">{borclu.borclu_adi || 'Borçlu Adı Yok'}</h4>
                    {borclu.borclu_tipi && (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                        {borclu.borclu_tipi}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {borclu.tc_vkn && (
                      <div>
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-1">TC/VKN</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{borclu.tc_vkn}</dd>
                      </div>
                    )}
                    {borclu.ticaret_sicil_no && (
                      <div>
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-1">Ticaret Sicil No</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{borclu.ticaret_sicil_no}</dd>
                      </div>
                    )}
                    {borclu.karar_turu && (
                      <div>
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-1">Karar Türü</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{borclu.karar_turu}</dd>
                      </div>
                    )}
                    {borclu.karar_tarihi && (
                      <div>
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-1">Karar Tarihi</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{borclu.karar_tarihi}</dd>
                      </div>
                    )}
                    {borclu.karar_baslangic_tarihi && (
                      <div>
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-1">Karar Başlangıç Tarihi</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{borclu.karar_baslangic_tarihi}</dd>
                      </div>
                    )}
                    {borclu.muhlet_suresi && (
                      <div>
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-1">Mühlet Süresi</dt>
                        <dd className="text-sm font-semibold text-gray-900 dark:text-white">{borclu.muhlet_suresi}</dd>
                      </div>
                    )}
                    {borclu.adres && (
                      <div className="md:col-span-2 lg:col-span-3">
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-1">Adres</dt>
                        <dd className="text-sm text-gray-900 dark:text-white">{borclu.adres}</dd>
                      </div>
                    )}
                    {borclu.karar_ozeti && (
                      <div className="md:col-span-2 lg:col-span-3 mt-2 pt-3 border-t border-gray-200 dark:border-gray-700">
                        <dt className="text-xs text-gray-600 dark:text-gray-400 mb-2">Karar Özeti</dt>
                        <dd className="text-sm text-gray-900 dark:text-gray-300 leading-relaxed bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">{borclu.karar_ozeti}</dd>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* İlan Metni */}
        {ilan.metin && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              İlan Metni
            </h3>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-5 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed border border-gray-200 dark:border-gray-600">
              {ilan.metin}
            </div>
          </div>
        )}
      </div>

      {/* Hata Bildirimi Modal */}
      {showReportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setShowReportModal(false)}>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center">
                <svg className="w-6 h-6 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Hata Bildir
              </h3>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Bu ilanda gördüğünüz hataları bize bildirin. Raporunuz incelenecektir.
            </p>

            {reportSuccess && (
              <div className="mb-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 px-4 py-3 rounded text-sm">
                {reportSuccess}
              </div>
            )}

            {reportError && (
              <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded text-sm">
                {reportError}
              </div>
            )}

            <form onSubmit={handleReportSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Hata Kategorisi
                </label>
                <select
                  name="kategori"
                  value={reportForm.kategori}
                  onChange={handleReportChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                >
                  <option value="yanlis_bilgi">Yanlış Bilgi</option>
                  <option value="eksik_bilgi">Eksik Bilgi</option>
                  <option value="kvkk_ihlali">KVKK İhlali (TC, Adres vb.)</option>
                  <option value="diger">Diğer</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Açıklama (En az 10 karakter)
                </label>
                <textarea
                  name="aciklama"
                  value={reportForm.aciklama}
                  onChange={handleReportChange}
                  rows="4"
                  placeholder="Lütfen hatayı detaylı bir şekilde açıklayın..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"
                  minLength={10}
                  maxLength={1000}
                  required
                ></textarea>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {reportForm.aciklama.length}/1000 karakter
                </p>
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  İptal
                </button>
                <button
                  type="submit"
                  disabled={reportLoading}
                  className="flex-1 px-4 py-2 bg-red-500 dark:bg-red-600 text-white rounded-lg hover:bg-red-600 dark:hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {reportLoading ? 'Gönderiliyor...' : 'Gönder'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default IlanDetay

