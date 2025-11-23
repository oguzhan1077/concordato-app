import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API_URL = '/api';

function IlanList() {
  const [ilanlar, setIlanlar] = useState([]);
  const [stats, setStats] = useState(null);
  const [gunlukIlanlar, setGunlukIlanlar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sehirler, setSehirler] = useState([]);
  const [filterSehir, setFilterSehir] = useState('Tümü');
  const [search, setSearch] = useState('');
  const [baslangicTarihi, setBaslangicTarihi] = useState('');
  const [bitisTarihi, setBitisTarihi] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const pageSize = 12;

  useEffect(() => {
    // Filtre veya sayfa değiştiğinde scroll pozisyonunu en üste al
    window.scrollTo(0, 0);
    
    fetchData();
    fetchStats();
    fetchSehirler();
  }, [filterSehir, currentPage, baslangicTarihi, bitisTarihi, search]);

  useEffect(() => {
    fetchGunlukIlanlar();
  }, []); // Sadece sayfa yüklendiğinde bir kez çalışır

  const fetchData = async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * pageSize;
      let url = `${API_URL}/ilanlar?skip=${skip}&limit=${pageSize}`;
      if (filterSehir !== 'Tümü') url += `&sehir=${filterSehir}`;
      if (search) url += `&search=${search}`;
      if (baslangicTarihi) url += `&baslangic_tarihi=${baslangicTarihi}`;
      if (bitisTarihi) url += `&bitis_tarihi=${bitisTarihi}`;
      
      const res = await axios.get(url);
      setIlanlar(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      // Sadece geliştirme modunda hata göster
      if (import.meta.env.DEV) {
        console.error("Veri çekme hatası:", err);
      }
      setIlanlar([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_URL}/stats`);
      setStats(res.data);
    } catch (err) {
      // Stats isteğe bağlı, hata varsa gösterme
      if (import.meta.env.DEV) {
        console.warn("Stats yüklenemedi:", err.message);
      }
    }
  };

  const fetchSehirler = async () => {
    try {
      const res = await axios.get(`${API_URL}/sehirler`);
      setSehirler(['Tümü', ...res.data]);
    } catch (err) {
      // Şehirler yüklenemezse sadece "Tümü" göster
      setSehirler(['Tümü']);
      if (import.meta.env.DEV) {
        console.warn("Şehirler yüklenemedi:", err.message);
      }
    }
  };

  const fetchGunlukIlanlar = async () => {
    try {
      const res = await axios.get(`${API_URL}/stats/gunluk-ilanlar`);
      setGunlukIlanlar(res.data);
    } catch (err) {
      if (import.meta.env.DEV) {
        console.warn("Günlük ilanlar yüklenemedi:", err.message);
      }
      setGunlukIlanlar([]);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchData();
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = (newSehir) => {
    setFilterSehir(newSehir);
    setCurrentPage(1);
  };

  const handleTarihChange = () => {
    setCurrentPage(1);
  };

  const handleTemizle = () => {
    setFilterSehir('Tümü');
    setSearch('');
    setBaslangicTarihi('');
    setBitisTarihi('');
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6 transition-colors">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Güncel İlanlar</h1>
          <p className="text-base text-gray-600 dark:text-gray-400">Konkordato ve iflas ilanlarını takip edin</p>
        </header>
        {/* İstatistik Kartları */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-200 hover:border-blue-300 dark:hover:border-blue-600">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Toplam İlan</h3>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {(filterSehir !== 'Tümü' || search || baslangicTarihi || bitisTarihi) 
                  ? totalItems.toLocaleString('tr-TR') 
                  : stats.total_ilan.toLocaleString('tr-TR')}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-200 hover:border-green-300 dark:hover:border-green-600">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">En Yoğun Şehir</h3>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">{stats.top_cities[0]?.sehir || '-'}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-200 hover:border-purple-300 dark:hover:border-purple-600">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Son Güncelleme</h3>
              <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">{stats.last_update}</p>
            </div>
          </div>
        )}

        {/* Günlük İlan Grafiği */}
        {gunlukIlanlar.length > 0 && (
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Bu Ayki Günlük İlan Sayıları
              <span className="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
                ({new Date().toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' })})
              </span>
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart 
                data={gunlukIlanlar}
                margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                <XAxis 
                  dataKey="gun" 
                  stroke="#6B7280"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="#6B7280"
                  style={{ fontSize: '12px' }}
                  allowDecimals={false}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F9FAFB'
                  }}
                  labelStyle={{ color: '#F9FAFB' }}
                />
                <Legend 
                  wrapperStyle={{ fontSize: '14px' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="sayi" 
                  name="İlan Sayısı"
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={{ fill: '#3B82F6', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Filtreler */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Filtreler</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Şehir</label>
              <select 
                value={filterSehir} 
                onChange={(e) => handleFilterChange(e.target.value)}
                className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all hover:border-blue-400 dark:hover:border-blue-500"
              >
                {sehirler.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Başlangıç Tarihi</label>
              <input 
                type="date"
                value={baslangicTarihi}
                onChange={(e) => {
                  setBaslangicTarihi(e.target.value);
                  handleTarihChange();
                }}
                className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all hover:border-blue-400 dark:hover:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bitiş Tarihi</label>
              <input 
                type="date"
                value={bitisTarihi}
                onChange={(e) => {
                  setBitisTarihi(e.target.value);
                  handleTarihChange();
                }}
                min={baslangicTarihi || undefined}
                className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all hover:border-blue-400 dark:hover:border-blue-500"
              />
            </div>
            
            <div className="flex items-end gap-2 lg:col-span-2">
              <form onSubmit={handleSearch} className="flex-1 flex gap-2">
                <input 
                  type="text" 
                  value={search} 
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="İlan, borçlu ara..."
                  className="flex-1 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all hover:border-blue-400 dark:hover:border-blue-500"
                />
                <button type="submit" className="bg-blue-600 dark:bg-blue-700 text-white px-6 py-2.5 text-sm font-medium rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800 transition-all shadow-sm hover:shadow-md whitespace-nowrap">
                  Ara
                </button>
              </form>
              <button
                onClick={handleTemizle}
                className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-4 py-2.5 text-sm font-medium rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-all border border-gray-300 dark:border-gray-600 hover:shadow-sm whitespace-nowrap"
              >
                Temizle
              </button>
            </div>
          </div>
        </div>

        {/* Tablo */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-700">
                <tr>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">#</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Tarih</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">İlan No</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Başlık</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Şehir</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Borçlu</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">İşlem</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {loading ? (
                   <tr><td colSpan="7" className="px-6 py-12 text-center text-base text-gray-500 dark:text-gray-400">
                     <div className="flex items-center justify-center">
                       <svg className="animate-spin h-6 w-6 mr-3 text-blue-600 dark:text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                         <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                         <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                       </svg>
                       Yükleniyor...
                     </div>
                   </td></tr>
                ) : ilanlar.length === 0 ? (
                  <tr><td colSpan="7" className="px-6 py-12 text-center text-base text-gray-500 dark:text-gray-400">
                    <div className="flex flex-col items-center">
                      <svg className="h-12 w-12 text-gray-400 dark:text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      İlan bulunamadı
                    </div>
                  </td></tr>
                ) : ilanlar.map((ilan, index) => (
                  <tr key={ilan.id} className="hover:bg-blue-50/50 dark:hover:bg-gray-700/50 transition-all duration-150 cursor-pointer group">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-bold text-gray-500 dark:text-gray-400">
                      {(currentPage - 1) * pageSize + index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300 font-medium">{ilan.yayin_tarihi || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-white">{ilan.ilan_no}</td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300 truncate max-w-xs group-hover:text-blue-700 dark:group-hover:text-blue-400 transition-colors" title={ilan.baslik || ''}>
                      {ilan.baslik || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 group-hover:text-blue-800 dark:group-hover:text-blue-300 transition-colors">
                        {ilan.sehir || '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300 truncate max-w-xs" title={ilan.borclular?.map(b => b.borclu_adi).join(', ') || ''}>
                      {ilan.borclular?.map(b => b.borclu_adi).join(', ') || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link 
                        to={`/ilan/${ilan.id}`}
                        className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-white bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-600 dark:hover:bg-blue-700 rounded-lg transition-all duration-200 hover:shadow-md"
                      >
                        Detay →
                      </Link>
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
                    Toplam <span className="font-bold text-gray-900 dark:text-white">{totalItems}</span> ilan • 
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
  )
}

export default IlanList

