from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

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

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class HataRaporu(Base):
    __tablename__ = "hata_raporlari"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ilan_id = Column(Integer, ForeignKey('ilanlar.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    kategori = Column(String(100), nullable=False)  # "yanlis_bilgi", "eksik_bilgi", "diger"
    aciklama = Column(Text, nullable=False)
    durum = Column(String(50), default="beklemede")  # "beklemede", "inceleniyor", "cozuldu", "reddedildi"
    olusturma_tarihi = Column(DateTime, default=func.now())
    guncellenme_tarihi = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # İlişkiler
    ilan = relationship("Ilan")
    user = relationship("User")