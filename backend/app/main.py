from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import re

from . import models, schemas, database, auth

# Database tablolarını oluştur
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Konkordato Takip API")

# Auth Router'ı ekle
app.include_router(auth.router, tags=["auth"])

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production'da spesifik domainleri belirtin
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

class IlanListResponse(BaseModel):
    items: List[schemas.Ilan]
    total: int
    page: int
    page_size: int
    total_pages: int

def parse_tarih(tarih_str):
    """GG.AA.YYYY formatındaki tarihi datetime'a çevirir"""
    if not tarih_str:
        return None
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
    skip: int = 0, 
    limit: int = 20, 
    sehir: Optional[str] = None,
    search: Optional[str] = None,
    baslangic_tarihi: Optional[str] = None,
    bitis_tarihi: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Ilan)
    
    if sehir and sehir != "Tümü":
        query = query.filter(models.Ilan.sehir == sehir)
        
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.Ilan.baslik.like(search_term)) | 
            (models.Ilan.ilan_no.like(search_term)) |
            (models.Ilan.metin.like(search_term))
        )
    
    # Tarih filtreleme
    if baslangic_tarihi:
        baslangic_dt = parse_tarih(baslangic_tarihi)
        if baslangic_dt:
            # Tarih string'lerini karşılaştırmak için tüm ilanları çekip filtreleme yapıyoruz
            # Daha iyi performans için veritabanında tarih alanını DATE olarak saklamak daha iyi olur
            # Şimdilik Python tarafında filtreleme yapıyoruz
            pass
    
    if bitis_tarihi:
        bitis_dt = parse_tarih(bitis_tarihi)
        if bitis_dt:
            pass
    
    # Tüm ilanları çek (tarih filtresi için)
    all_ilanlar = query.all()
    
    # Tarih filtresi uygula (eğer varsa)
    if baslangic_tarihi or bitis_tarihi:
        filtered_ilanlar = []
        for ilan in all_ilanlar:
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
        
        # Filtrelenmiş listeyi kullan
        total = len(filtered_ilanlar)
        # Sıralama
        filtered_ilanlar.sort(key=lambda x: (parse_tarih(x.yayin_tarihi) or datetime.min, x.id), reverse=True)
        # Sayfalama
        ilanlar = filtered_ilanlar[skip:skip+limit]
    else:
        # Tarih filtresi yoksa normal sorgu
        total = query.count()
        ilanlar = query.order_by(models.Ilan.yayin_tarihi.desc(), models.Ilan.id.desc()).offset(skip).limit(limit).all()
    
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit  # Ceiling division
    
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
    last_update = last_ilan.eklenme_tarihi.strftime("%d.%m.%Y %H:%M") if last_ilan else "-"
    
    return {
        "total_ilan": total_ilan,
        "top_cities": top_cities,
        "last_update": last_update
    }

@app.get("/sehirler")
def get_sehirler(db: Session = Depends(get_db)):
    sehirler = db.query(models.Ilan.sehir).distinct().order_by(models.Ilan.sehir).all()
    return [s[0] for s in sehirler if s[0]]

