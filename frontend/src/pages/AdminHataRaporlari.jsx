import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = '/api';

function AdminHataRaporlari() {
  const navigate = useNavigate();
  const [raporlar, setRaporlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [durumFilter, setDurumFilter] = useState('Tümü');
  const [isAdmin, setIsAdmin] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [openDropdownId, setOpenDropdownId] = useState(null);
  const pageSize = 20;

  // Sayfa yüklendiğinde güvenlik kontrolü
  useEffect(() => {
    window.scrollTo(0, 0);
    checkAdminAndFetch();
  }, [durumFilter, currentPage]);

  // Dışarı tıklama kontrolü
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (openDropdownId && !event.target.closest('.action-dropdown')) {
        setOpenDropdownId(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openDropdownId]);

  const checkAdminAndFetch = async () => {
    setLoading(true);
    try {
      // 1. Önce kullanıcı yetkisini kontrol et
      const userRes = await axios.get(`${API_URL}/users/me`);
      
      if (!userRes.data.is_superuser) {
        navigate('/', { replace: true });
        return;
      }
      
      setIsAdmin(true);

      // 2. Yetkili ise raporları çek (sayfalama ile)
      const skip = (currentPage - 1) * pageSize;
      let url = `${API_URL}/admin/hata-raporlari?skip=${skip}&limit=${pageSize}`;
      if (durumFilter !== 'Tümü') {
        url += `&durum=${durumFilter}`;
      }
      
      const res = await axios.get(url);
      setRaporlar(res.data.items);
      setTotalItems(res.data.total);
      setTotalPages(res.data.total_pages);
      
    } catch (err) {
      console.error("Admin erişim hatası:", err);
      navigate('/', { replace: true });
    } finally {
      setLoading(false);
    }
  };

  const updateDurum = async (raporId, yeniDurum) => {
    try {
      await axios.patch(`${API_URL}/admin/hata-raporlari/${raporId}?yeni_durum=${yeniDurum}`);
      setRaporlar(raporlar.map(r => 
        r.id === raporId ? { ...r, durum: yeniDurum } : r
      ));
    } catch (err) {
      alert('Durum güncellenemedi: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = (newDurum) => {
    setDurumFilter(newDurum);
    setCurrentPage(1);
  };

  // Renk kodları ve helper fonksiyonlar
  const getDurumBadgeColor = (durum) => {
    const colors = {
      beklemede: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
      inceleniyor: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      cozuldu: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      reddedildi: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    };
    return colors[durum] || 'bg-gray-100 text-gray-800';
  };

  const getDurumLabel = (durum) => {
    const labels = {
      beklemede: 'Beklemede',
      inceleniyor: 'İnceleniyor',
      cozuldu: 'Çözüldü',
      reddedildi: 'Reddedildi'
    };
    return labels[durum] || durum;
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-500">Yükleniyor...</div>;
  }

  if (!isAdmin) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6 transition-colors">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
          <div>
            <Link to="/" className="text-blue-600 dark:text-blue-400 hover:underline mb-1 inline-block text-sm">
              ← Ana Sayfaya Dön
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Hata Raporları</h1>
          </div>
          
          {/* Filtre */}
          <div className="flex items-center">
            <label className="mr-2 text-sm text-gray-600 dark:text-gray-400 font-medium">Durum:</label>
            <select
              value={durumFilter}
              onChange={(e) => handleFilterChange(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="Tümü">Tümü</option>
              <option value="beklemede">Beklemede</option>
              <option value="inceleniyor">İnceleniyor</option>
              <option value="cozuldu">Çözüldü</option>
              <option value="reddedildi">Reddedildi</option>
            </select>
          </div>
        </div>

        {/* Tablo - Sticky Header ile */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden overflow-visible">
          <div className="overflow-x-visible">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-700 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-20">#</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-24">Durum</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-40">Kullanıcı</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-32">Kategori</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-24">İlan No</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-32">Tarih</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-48">Açıklama</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider w-20">İşlem</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan="8" className="px-6 py-12 text-center text-base text-gray-500 dark:text-gray-400">
                      <div className="flex items-center justify-center">
                        <svg className="animate-spin h-6 w-6 mr-3 text-blue-600 dark:text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Yükleniyor...
                      </div>
                    </td>
                  </tr>
                ) : raporlar.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="px-6 py-12 text-center text-base text-gray-500 dark:text-gray-400">
                      <div className="flex flex-col items-center">
                        <svg className="h-12 w-12 text-gray-400 dark:text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {durumFilter === 'Tümü' ? 'Henüz hiç rapor yok.' : 'Bu filtrede rapor bulunamadı.'}
                      </div>
                    </td>
                  </tr>
                ) : raporlar.map((rapor, index) => (
                  <tr key={rapor.id} className="hover:bg-blue-50/50 dark:hover:bg-gray-700/50 transition-all duration-150 group">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-bold text-gray-500 dark:text-gray-400">
                      {(currentPage - 1) * pageSize + index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDurumBadgeColor(rapor.durum)}`}>
                        {getDurumLabel(rapor.durum)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                      <div className="flex flex-col">
                        <span className="font-medium">{rapor.user?.full_name || '-'}</span>
                        <span className="text-xs text-gray-400 dark:text-gray-500">{rapor.user?.email || '-'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                      {rapor.kategori.replace('_', ' ').toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link 
                        to={`/ilan/${rapor.ilan_id}`}
                        className="text-sm font-semibold text-blue-600 dark:text-blue-400 hover:underline"
                        target="_blank"
                      >
                        #{rapor.ilan_id}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300 font-medium">
                      {new Date(rapor.olusturma_tarihi).toLocaleDateString('tr-TR')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300 truncate max-w-md group-hover:text-blue-700 dark:group-hover:text-blue-400 transition-colors" title={rapor.aciklama}>
                      {rapor.aciklama}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center relative action-dropdown">
                      <button
                        onClick={() => setOpenDropdownId(openDropdownId === rapor.id ? null : rapor.id)}
                        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-blue-600 transition-colors"
                        title="Durumu Güncelle"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>

                      {openDropdownId === rapor.id && (
                        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-xl z-50 border border-gray-200 dark:border-gray-700 overflow-hidden transform origin-top-right">
                          <div className="py-1">
                            {['beklemede', 'inceleniyor', 'cozuldu', 'reddedildi'].map((status) => (
                              <button
                                key={status}
                                onClick={() => {
                                  updateDurum(rapor.id, status);
                                  setOpenDropdownId(null);
                                }}
                                className={`w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2 ${
                                  rapor.durum === status ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium' : 'text-gray-700 dark:text-gray-300'
                                }`}
                              >
                                <span className={`w-2 h-2 rounded-full ${
                                  status === 'beklemede' ? 'bg-yellow-400' :
                                  status === 'inceleniyor' ? 'bg-blue-400' :
                                  status === 'cozuldu' ? 'bg-green-400' :
                                  'bg-red-400'
                                }`}></span>
                                {getDurumLabel(status)}
                                {rapor.durum === status && (
                                  <svg className="w-4 h-4 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                )}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Sayfalama */}
          {totalPages > 1 && (
            <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 flex items-center justify-between border-t border-gray-200 dark:border-gray-600">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
                >
                  ← Önceki
                </button>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
                >
                  Sonraki →
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Toplam <span className="font-bold text-gray-900 dark:text-white">{totalItems}</span> rapor • 
                    Sayfa <span className="font-bold text-gray-900 dark:text-white">{(currentPage - 1) * pageSize + 1}</span>
                    {' - '}
                    <span className="font-bold text-gray-900 dark:text-white">
                      {Math.min(currentPage * pageSize, totalItems)}
                    </span>
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-lg shadow-sm -space-x-px" aria-label="Pagination">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-3 py-2 rounded-l-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                    >
                      <span className="sr-only">Önceki</span>
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                    
                    {/* Sayfa numaraları */}
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium transition-all ${
                            currentPage === pageNum
                              ? 'z-10 bg-blue-600 dark:bg-blue-700 border-blue-600 dark:border-blue-700 text-white hover:bg-blue-700 dark:hover:bg-blue-800'
                              : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                    
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-3 py-2 rounded-r-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                    >
                      <span className="sr-only">Sonraki</span>
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminHataRaporlari;
