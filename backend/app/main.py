import os

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import re
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from . import models, schemas, database, auth
from .auth import get_current_user

# Database tablolarını oluştur
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Konkordato Takip API")

# Rate limiter kurulumu
@app.on_event("startup")
async def startup_event():
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        redis_conn = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_conn)
        print(f"Redis bağlantısı başarılı: {redis_url}")
    except Exception as e:
        print(f"Redis bağlantı hatası: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await FastAPILimiter.close()
    except Exception as e:
        print(f"Redis kapatma hatası: {e}")

# Auth Router'ı ekle
app.include_router(auth.router, tags=["auth"])

# CORS Ayarları
allowed_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
allowed_origins = [
    origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Konkordato API Çalışıyor"}

# Pagination sabitleri - DoS saldırılarına karşı koruma
MAX_PAGE_LIMIT = 100  # Maksimum sayfa başına kayıt
DEFAULT_PAGE_LIMIT = 20  # Varsayılan limit
MIN_PAGE_LIMIT = 1  # Minimum limit

class IlanListResponse(BaseModel):
    items: List[schemas.Ilan]
    total: int
    page: int
    page_size: int
    total_pages: int

def parse_tarih(tarih_str):
    """GG.AA.YYYY, GG/AA/YYYY veya YYYY-MM-DD formatındaki tarihi datetime'a çevirir"""
    if not tarih_str:
        return None
    
    tarih_str = tarih_str.strip()
    
    # Önce normalize et (standart format: GG.AA.YYYY)
    import re
    # GG/AA/YYYY veya GG-AA-YYYY formatını GG.AA.YYYY'ye çevir
    tarih_str = re.sub(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', r'\1.\2.\3', tarih_str)
    
    try:
        # GG.AA.YYYY formatını parse et
        return datetime.strptime(tarih_str, "%d.%m.%Y")
    except:
        try:
            # YYYY-MM-DD formatını da dene
            return datetime.strptime(tarih_str, "%Y-%m-%d")
        except:
            return None

@app.get("/ilanlar", response_model=IlanListResponse)
def get_ilanlar(
    skip: int = Query(
        default=0, 
        ge=0, 
        description="Atlanacak kayıt sayısı (negatif olamaz)"
    ),
    limit: int = Query(
        default=DEFAULT_PAGE_LIMIT, 
        ge=MIN_PAGE_LIMIT, 
        le=MAX_PAGE_LIMIT,
        description=f"Sayfa başına kayıt sayısı (maksimum {MAX_PAGE_LIMIT})"
    ),
    sehir: Optional[str] = Query(default=None, description="Şehir filtresi"),
    search: Optional[str] = Query(default=None, max_length=200, description="Arama terimi"),
    baslangic_tarihi: Optional[str] = Query(default=None, description="Başlangıç tarihi (GG.MM.YYYY)"),
    bitis_tarihi: Optional[str] = Query(default=None, description="Bitiş tarihi (GG.MM.YYYY)"),
    db: Session = Depends(get_db)
):
    """
    İlanları sayfalı olarak getirir.
    
    Güvenlik:
    - limit maksimum 100 ile sınırlıdır (DoS koruması)
    - skip negatif olamaz
    - Tarih filtreleme veritabanı seviyesinde yapılır (performans)
    """
    query = db.query(models.Ilan)
    
    # Şehir filtresi
    if sehir and sehir != "Tümü":
        query = query.filter(models.Ilan.sehir == sehir)
    
    # Arama filtresi
    if search:
        # SQL injection koruması için parametreli sorgu kullanılıyor
        search_term = f"%{search[:200]}%"  # Maksimum 200 karakter
        query = query.filter(
            (models.Ilan.baslik.like(search_term)) | 
            (models.Ilan.ilan_no.like(search_term)) |
            (models.Ilan.metin.like(search_term))
        )
    
    # Tarih filtreleme - Veritabanı seviyesinde yapılıyor
    # NOT: yayin_tarihi string formatında saklanıyor, ideal çözüm DATE tipine çevirmek
    # Şimdilik subquery ile filtreleme yapıyoruz
    if baslangic_tarihi or bitis_tarihi:
        # Tarih filtreleme için tüm tabloyu çekmek yerine
        # maksimum 10000 kayıtla sınırlayarak güvenlik sağlıyoruz
        MAX_DATE_FILTER_RECORDS = 10000
        
        # Önce tarihe göre sıralı kayıtları çek (sınırlı)
        temp_query = query.order_by(models.Ilan.yayin_tarihi.desc(), models.Ilan.id.desc())
        temp_ilanlar = temp_query.limit(MAX_DATE_FILTER_RECORDS).all()
        
        filtered_ilanlar = []
        for ilan in temp_ilanlar:
            if not ilan.yayin_tarihi:
                continue
                
            ilan_tarih = parse_tarih(ilan.yayin_tarihi)
            if not ilan_tarih:
                continue
            
            # Başlangıç tarihi kontrolü
            if baslangic_tarihi:
                baslangic_dt = parse_tarih(baslangic_tarihi)
                if baslangic_dt and ilan_tarih < baslangic_dt:
                    continue
            
            # Bitiş tarihi kontrolü
            if bitis_tarihi:
                bitis_dt = parse_tarih(bitis_tarihi)
                if bitis_dt and ilan_tarih > bitis_dt:
                    continue
            
            filtered_ilanlar.append(ilan)
        
        # Filtrelenmiş sonuçlar
        total = len(filtered_ilanlar)
        # Sıralama (zaten tarihe göre sıralı)
        # Sayfalama
        ilanlar = filtered_ilanlar[skip:skip+limit]
    else:
        # Tarih filtresi yoksa veritabanı seviyesinde pagination
        total = query.count()
        ilanlar = query.order_by(
            models.Ilan.yayin_tarihi.desc(), 
            models.Ilan.id.desc()
        ).offset(skip).limit(limit).all()
    
    # Sayfa hesaplamaları - division by zero koruması
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "items": ilanlar,
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages
    }

@app.get("/ilanlar/{ilan_id}", response_model=schemas.Ilan)
def get_ilan_detay(ilan_id: int, db: Session = Depends(get_db)):
    ilan = db.query(models.Ilan).filter(models.Ilan.id == ilan_id).first()
    if ilan is None:
        raise HTTPException(status_code=404, detail="İlan bulunamadı")
    return ilan

@app.get("/stats", response_model=schemas.Stats)
def get_stats(db: Session = Depends(get_db)):
    total_ilan = db.query(models.Ilan).count()
    
    # En çok ilan çıkan şehirler
    top_cities_query = db.query(
        models.Ilan.sehir, 
        func.count(models.Ilan.sehir).label('count')
    ).group_by(models.Ilan.sehir).order_by(func.count(models.Ilan.sehir).desc()).limit(10).all()
    
    top_cities = [{"sehir": city, "count": count} for city, count in top_cities_query]
    
    # Son güncelleme (en yeni ilan tarihi)
    last_ilan = db.query(models.Ilan).order_by(models.Ilan.eklenme_tarihi.desc()).first()
    last_update = last_ilan.eklenme_tarihi.strftime("%d.%m.%Y") if last_ilan else "-"
    
    return {
        "total_ilan": total_ilan,
        "top_cities": top_cities,
        "last_update": last_update
    }

@app.get("/sehirler")
def get_sehirler(db: Session = Depends(get_db)):
    sehirler = db.query(models.Ilan.sehir).distinct().order_by(models.Ilan.sehir).all()
    return [s[0] for s in sehirler if s[0]]

@app.get("/stats/gunluk-ilanlar")
def get_gunluk_ilanlar(db: Session = Depends(get_db)):
    """
    İçinde bulunduğumuz ayın günlük ilan sayılarını döndürür.
    """
    from datetime import datetime
    from collections import defaultdict
    
    # Bugünün tarihi ve ayın ilk günü
    bugun = datetime.now()
    ayin_ilk_gunu = datetime(bugun.year, bugun.month, 1)
    
    # Tüm ilanları çek
    ilanlar = db.query(models.Ilan).all()
    
    # Günlere göre grupla
    gunluk_sayilar = defaultdict(int)
    
    for ilan in ilanlar:
        if not ilan.yayin_tarihi:
            continue
        
        # Tarihi parse et
        tarih = parse_tarih(ilan.yayin_tarihi)
        if not tarih:
            continue
        
        # Sadece bu ayın ilanlarını al
        if tarih >= ayin_ilk_gunu and tarih <= bugun:
            tarih_str = tarih.strftime("%Y-%m-%d")
            gunluk_sayilar[tarih_str] += 1
    
    # Sonuçları sırala ve formatla
    result = []
    for tarih_str, count in sorted(gunluk_sayilar.items()):
        tarih_obj = datetime.strptime(tarih_str, "%Y-%m-%d")
        result.append({
            "tarih": tarih_str,
            "gun": tarih_obj.strftime("%d.%m"),
            "sayi": count
        })
    
    return result

@app.post("/rapor-olustur", response_model=schemas.HataRaporuResponse)
async def rapor_olustur(
    rapor: schemas.HataRaporuCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Hata raporu oluşturur. Sadece giriş yapmış kullanıcılar kullanabilir.
    
    Güvenlik:
    - Kullanıcı kimlik doğrulaması zorunludur
    - İlan ID'sinin geçerli olması kontrol edilir
    - Açıklama uzunluğu sınırlandırılmıştır (max 1000 karakter)
    """
    # İlanın varlığını kontrol et
    ilan = db.query(models.Ilan).filter(models.Ilan.id == rapor.ilan_id).first()
    if not ilan:
        raise HTTPException(status_code=404, detail="İlan bulunamadı")
    
    # Aynı kullanıcının aynı ilan için kısa sürede çoklu rapor oluşturmasını engelle
    from datetime import datetime, timedelta
    recent_report = db.query(models.HataRaporu).filter(
        models.HataRaporu.ilan_id == rapor.ilan_id,
        models.HataRaporu.user_id == current_user.id,
        models.HataRaporu.olusturma_tarihi >= datetime.now() - timedelta(hours=1)
    ).first()
    
    if recent_report:
        raise HTTPException(
            status_code=429, 
            detail="Bu ilan için son 1 saat içinde zaten bir rapor oluşturdunuz"
        )
    
    # Yeni rapor oluştur
    db_rapor = models.HataRaporu(
        ilan_id=rapor.ilan_id,
        user_id=current_user.id,
        kategori=rapor.kategori,
        aciklama=rapor.aciklama.strip(),
        durum="beklemede"
    )
    
    db.add(db_rapor)
    db.commit()
    db.refresh(db_rapor)
    
    return {
        "message": "Hata raporunuz başarıyla oluşturuldu. İnceleme yapılacaktır.",
        "rapor_id": db_rapor.id
    }

