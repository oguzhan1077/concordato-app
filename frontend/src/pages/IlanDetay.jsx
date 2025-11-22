import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = '/api';

function IlanDetay() {
  const { id } = useParams();
  const [ilan, setIlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchIlanDetay();
  }, [id]);

  const fetchIlanDetay = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_URL}/ilanlar/${id}`);
      setIlan(res.data);
    } catch (err) {
      console.error("İlan detay hatası:", err);
      setError("İlan bulunamadı");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">Yükleniyor...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !ilan) {
    return (
      <div className="p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-red-600 mb-4">{error || "İlan bulunamadı"}</p>
            <Link to="/" className="text-blue-600 hover:underline">
              ← Ana Sayfaya Dön
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link 
            to="/" 
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Ana Sayfaya Dön
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">İlan Detayları</h1>
        </div>

        {/* İlan Bilgileri */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">{ilan.baslik || 'Başlık Yok'}</h2>
            <p className="text-sm text-gray-500">İlan No: <span className="font-medium text-gray-900">{ilan.ilan_no}</span></p>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Temel Bilgiler</h3>
                <dl className="space-y-2">
                  <div>
                    <dt className="text-xs text-gray-500">Yayın Tarihi</dt>
                    <dd className="text-sm text-gray-900 font-medium">{ilan.yayin_tarihi || '-'}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">Şehir</dt>
                    <dd className="text-sm text-gray-900">{ilan.sehir || '-'}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">İlçe</dt>
                    <dd className="text-sm text-gray-900">{ilan.ilce || '-'}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">Kurum</dt>
                    <dd className="text-sm text-gray-900">{ilan.kurum || '-'}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">İlan Türü</dt>
                    <dd className="text-sm text-gray-900">{ilan.ilan_turu || '-'}</dd>
                  </div>
                </dl>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">İşlemler</h3>
                {ilan.link && (
                  <a 
                    href={ilan.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
                  >
                    Orijinal İlanı Görüntüle
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}
              </div>
            </div>

            {/* İlan Metni */}
            {ilan.metin && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">İlan Metni</h3>
                <div className="bg-gray-50 rounded p-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {ilan.metin}
                </div>
              </div>
            )}

            {/* Borçlu Bilgileri */}
            {ilan.borclular && ilan.borclular.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-4">Borçlu Bilgileri</h3>
                <div className="space-y-4">
                  {ilan.borclular.map((borclu, index) => (
                    <div key={borclu.id || index} className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">{borclu.borclu_adi || 'Borçlu Adı Yok'}</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        <div>
                          <dt className="text-gray-500 mb-1">Borçlu Tipi</dt>
                          <dd className="text-gray-900 font-medium">{borclu.borclu_tipi || '-'}</dd>
                        </div>
                        {borclu.tc_vkn && (
                          <div>
                            <dt className="text-gray-500 mb-1">TC/VKN</dt>
                            <dd className="text-gray-900 font-medium">{borclu.tc_vkn}</dd>
                          </div>
                        )}
                        {borclu.ticaret_sicil_no && (
                          <div>
                            <dt className="text-gray-500 mb-1">Ticaret Sicil No</dt>
                            <dd className="text-gray-900 font-medium">{borclu.ticaret_sicil_no}</dd>
                          </div>
                        )}
                        {borclu.adres && (
                          <div className="md:col-span-2">
                            <dt className="text-gray-500 mb-1">Adres</dt>
                            <dd className="text-gray-900">{borclu.adres}</dd>
                          </div>
                        )}
                        {borclu.karar_turu && (
                          <div>
                            <dt className="text-gray-500 mb-1">Karar Türü</dt>
                            <dd className="text-gray-900 font-medium">{borclu.karar_turu}</dd>
                          </div>
                        )}
                        {borclu.karar_tarihi && (
                          <div>
                            <dt className="text-gray-500 mb-1">Karar Tarihi</dt>
                            <dd className="text-gray-900">{borclu.karar_tarihi}</dd>
                          </div>
                        )}
                        {borclu.mahkeme_adi && (
                          <div>
                            <dt className="text-gray-500 mb-1">Mahkeme</dt>
                            <dd className="text-gray-900">{borclu.mahkeme_adi}</dd>
                          </div>
                        )}
                        {borclu.dosya_esas_no && (
                          <div>
                            <dt className="text-gray-500 mb-1">Dosya Esas No</dt>
                            <dd className="text-gray-900">{borclu.dosya_esas_no}</dd>
                          </div>
                        )}
                        {borclu.karar_ozeti && (
                          <div className="md:col-span-2 mt-2 pt-2 border-t border-gray-200">
                            <dt className="text-gray-500 mb-1">Karar Özeti</dt>
                            <dd className="text-gray-900 text-sm leading-relaxed">{borclu.karar_ozeti}</dd>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default IlanDetay

