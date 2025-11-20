from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
import sys

# Veritabanı URL'i oluşturma
# Şifre boş ise :password kısmını atla veya boş string geç
if DB_PASSWORD:
    DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
else:
    DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}@{DB_HOST}/{DB_NAME}"

Base = declarative_base()

class Ilan(Base):
    __tablename__ = 'ilanlar'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ilan_no = Column(String(50), unique=True, nullable=False) # Benzersiz İlan No
    baslik = Column(String(255))
    sehir = Column(String(100))
    ilce = Column(String(100))
    kurum = Column(String(255))
    ilan_turu = Column(String(100))
    metin = Column(Text) # Uzun metin
    link = Column(String(500))
    yayin_tarihi = Column(String(50)) # İlanın yayınlanma tarihi
    eklenme_tarihi = Column(DateTime, default=func.now())

    # İlişki: Bir ilanın birden fazla analiz edilmiş borçlusu olabilir
    borclular = relationship("IlanBorclu", back_populates="ilan", cascade="all, delete-orphan")

class IlanBorclu(Base):
    __tablename__ = 'ilan_borclulari'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ilan_id = Column(Integer, ForeignKey('ilanlar.id'), nullable=False)
    
    # Analiz Sonuçları
    borclu_adi = Column(String(255))          # Kişi veya Şirket Adı
    borclu_tipi = Column(String(50))          # GERCEK_KISI veya TUZEL_KISI
    tc_vkn = Column(String(50))               # TC veya Vergi No
    ticaret_sicil_no = Column(String(100))
    adres = Column(Text)                      # Kayıtlı Merkez / Adres
    
    karar_turu = Column(String(100))          # Geçici Mühlet, İflas, Tasfiye vb.
    karar_ozeti = Column(Text)                # Yapay zeka tarafından oluşturulan kısa özet
    karar_tarihi = Column(String(50))         # Kararın verildiği Tarih
    karar_baslangic_tarihi = Column(String(50)) # Mühletin/Kararın işlemeye başladığı tarih
    muhlet_suresi = Column(String(100))       # "3 Ay", "1 Yıl" vb.
    mahkeme_adi = Column(String(255))
    dosya_esas_no = Column(String(100))
    komiserler = Column(Text)                 # Komiser isimleri
    durusma_tarihi = Column(String(100))      # Varsa duruşma tarihi
    
    analiz_tarihi = Column(DateTime, default=func.now())

    # İlişki
    ilan = relationship("Ilan", back_populates="borclular")

def get_db_session():
    """Veritabanı bağlantısını kurar ve oturum döndürür"""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        # Tabloları oluştur (Eğer yoksa)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"Veritabanı Bağlantı Hatası: {e}")
        print("Lütfen config.py dosyasındaki bilgilerin doğru olduğundan ve MySQL sunucusunun çalıştığından emin olun.")
        print(f"Denlenen URL: {DATABASE_URL.replace(DB_PASSWORD, '***') if DB_PASSWORD else DATABASE_URL}")
        sys.exit(1)

