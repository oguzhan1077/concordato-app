import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = '/api';

function IlanList() {
  const [ilanlar, setIlanlar] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sehirler, setSehirler] = useState([]);
  const [filterSehir, setFilterSehir] = useState('Tümü');
  const [search, setSearch] = useState('');
  const [baslangicTarihi, setBaslangicTarihi] = useState('');
  const [bitisTarihi, setBitisTarihi] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchData();
    fetchStats();
    fetchSehirler();
  }, [filterSehir, currentPage, baslangicTarihi, bitisTarihi]);

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
      console.error("Veri çekme hatası:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_URL}/stats`);
      setStats(res.data);
    } catch (err) {
      console.error("Stats hatası:", err);
    }
  };

  const fetchSehirler = async () => {
    try {
      const res = await axios.get(`${API_URL}/sehirler`);
      setSehirler(['Tümü', ...res.data]);
    } catch (err) {
      console.error("Şehirler hatası:", err);
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
    <div className="p-4">
      <div className="max-w-7xl mx-auto">
        <header className="mb-6">
          <h1 className="text-xl font-semibold text-gray-900 mb-1">Güncel İlanlar</h1>
          <p className="text-sm text-gray-500">Güncel konkordato ve iflas ilanları</p>
        </header>
        {/* İstatistik Kartları */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <h3 className="text-xs text-gray-500 mb-1">Toplam İlan</h3>
              <p className="text-xl font-semibold text-gray-900">{stats.total_ilan.toLocaleString('tr-TR')}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <h3 className="text-xs text-gray-500 mb-1">En Yoğun Şehir</h3>
              <p className="text-xl font-semibold text-gray-900">{stats.top_cities[0]?.sehir || '-'}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <h3 className="text-xs text-gray-500 mb-1">Son Güncelleme</h3>
              <p className="text-xl font-semibold text-gray-900">{stats.last_update}</p>
            </div>
          </div>
        )}

        {/* Filtreler */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 mb-3">
            <div>
              <label className="block text-xs text-gray-600 mb-1.5">Şehir</label>
              <select 
                value={filterSehir} 
                onChange={(e) => handleFilterChange(e.target.value)}
                className="w-full border border-gray-200 rounded px-2.5 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                {sehirler.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-gray-600 mb-1.5">Başlangıç Tarihi</label>
              <input 
                type="date"
                value={baslangicTarihi}
                onChange={(e) => {
                  setBaslangicTarihi(e.target.value);
                  handleTarihChange();
                }}
                className="w-full border border-gray-200 rounded px-2.5 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-600 mb-1.5">Bitiş Tarihi</label>
              <input 
                type="date"
                value={bitisTarihi}
                onChange={(e) => {
                  setBitisTarihi(e.target.value);
                  handleTarihChange();
                }}
                min={baslangicTarihi || undefined}
                className="w-full border border-gray-200 rounded px-2.5 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="flex items-end">
              <button
                onClick={handleTemizle}
                className="w-full bg-gray-100 text-gray-700 px-3 py-1.5 text-sm rounded hover:bg-gray-200 transition-colors border border-gray-200"
              >
                Temizle
              </button>
            </div>
            
            <div className="flex items-end">
              <form onSubmit={handleSearch} className="w-full flex gap-2">
                <input 
                  type="text" 
                  value={search} 
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Ara..."
                  className="flex-1 border border-gray-200 rounded px-2.5 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
                <button type="submit" className="bg-blue-600 text-white px-4 py-1.5 text-sm rounded hover:bg-blue-700 transition-colors">
                  Ara
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Tablo */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100">
              <thead className="bg-gray-50/50">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">Tarih</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">İlan No</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">Başlık</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">Şehir</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">Borçlu</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">İşlem</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {loading ? (
                   <tr><td colSpan="6" className="px-4 py-8 text-center text-sm text-gray-500">Yükleniyor...</td></tr>
                ) : ilanlar.length === 0 ? (
                  <tr><td colSpan="6" className="px-4 py-8 text-center text-sm text-gray-500">İlan bulunamadı</td></tr>
                ) : ilanlar.map((ilan) => (
                  <tr key={ilan.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-4 py-2.5 whitespace-nowrap text-xs text-gray-600">{ilan.yayin_tarihi || '-'}</td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-xs font-medium text-gray-900">{ilan.ilan_no}</td>
                    <td className="px-4 py-2.5 text-xs text-gray-700 truncate max-w-xs" title={ilan.baslik || ''}>
                      {ilan.baslik || '-'}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-xs text-gray-600">{ilan.sehir || '-'}</td>
                    <td className="px-4 py-2.5 text-xs text-gray-600 truncate max-w-xs" title={ilan.borclular?.map(b => b.borclu_adi).join(', ') || ''}>
                      {ilan.borclular?.map(b => b.borclu_adi).join(', ') || '-'}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap">
                      <Link 
                        to={`/ilan/${ilan.id}`}
                        className="text-xs text-blue-600 hover:text-blue-800 hover:underline font-medium"
                      >
                        Detay
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Sayfalama */}
          {totalPages > 1 && (
            <div className="bg-white px-4 py-2.5 flex items-center justify-between border-t border-gray-100 sm:px-4">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-medium rounded text-gray-600 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Önceki
                </button>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="ml-2 relative inline-flex items-center px-3 py-1.5 border border-gray-200 text-xs font-medium rounded text-gray-600 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Sonraki
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs text-gray-600">
                    Toplam <span className="font-semibold text-gray-900">{totalItems}</span> ilan • Sayfa{' '}
                    <span className="font-semibold text-gray-900">{(currentPage - 1) * pageSize + 1}</span>
                    {' - '}
                    <span className="font-semibold text-gray-900">
                      {Math.min(currentPage * pageSize, totalItems)}
                    </span>
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded border border-gray-200 -space-x-px" aria-label="Pagination">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-1.5 rounded-l border-r border-gray-200 bg-white text-xs font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                      <span className="sr-only">Önceki</span>
                      <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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
                          className={`relative inline-flex items-center px-3 py-1.5 border-r border-gray-200 text-xs font-medium transition-colors ${
                            currentPage === pageNum
                              ? 'z-10 bg-blue-50 text-blue-700 border-blue-200'
                              : 'bg-white text-gray-600 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                    
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-1.5 rounded-r bg-white text-xs font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                      <span className="sr-only">Sonraki</span>
                      <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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

