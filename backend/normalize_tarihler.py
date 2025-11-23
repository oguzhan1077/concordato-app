"""
Mevcut veritabanındaki tarih formatlarını standart hale getirir (GG.AA.YYYY)
Bu script bir kez çalıştırılmalıdır.
"""
import re
from app.database import SessionLocal
from app.models import Ilan, IlanBorclu

def normalize_tarih(tarih_str):
    """
    Tarih formatını standart hale getirir (GG.AA.YYYY)
    Desteklenen formatlar: 
    - 21/11/2025 -> 21.11.2025
    - 21.11.2025 -> 21.11.2025
    - 21-11-2025 -> 21.11.2025
    """
    if not tarih_str:
        return ""
    
    tarih_str = str(tarih_str).strip().replace(":", "").strip()
    
    # Boşlukları temizle
    tarih_str = " ".join(tarih_str.split())
    
    if not tarih_str:
        return ""
    
    # Farklı ayırıcıları normalize et
    # "/" veya "-" ile ayrılmış tarihleri "." ile değiştir
    # GG/AA/YYYY veya GG-AA-YYYY formatını GG.AA.YYYY'ye çevir
    tarih_str = re.sub(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', r'\1.\2.\3', tarih_str)
    
    # Eğer zaten "." ile ayrılmışsa ve format doğruysa olduğu gibi döndür
    if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', tarih_str):
        # Gün ve ayı 2 haneli yap (01.11.2025 gibi)
        parts = tarih_str.split('.')
        if len(parts) == 3:
            gun = parts[0].zfill(2)
            ay = parts[1].zfill(2)
            yil = parts[2]
            return f"{gun}.{ay}.{yil}"
        return tarih_str
    
    return tarih_str

def normalize_veritabani():
    """Veritabanındaki tüm tarihleri normalize eder"""
    session = SessionLocal()
    
    try:
        # İlanlar tablosundaki yayin_tarihi alanlarını normalize et
        print("İlanlar tablosundaki tarihler normalize ediliyor...")
        ilanlar = session.query(Ilan).all()
        ilan_guncelleme_sayisi = 0
        
        for ilan in ilanlar:
            if ilan.yayin_tarihi:
                normalized = normalize_tarih(ilan.yayin_tarihi)
                if normalized != ilan.yayin_tarihi:
                    print(f"  İlan {ilan.id} ({ilan.ilan_no}): '{ilan.yayin_tarihi}' -> '{normalized}'")
                    ilan.yayin_tarihi = normalized
                    ilan_guncelleme_sayisi += 1
        
        # İlanBorclu tablosundaki tarih alanlarını normalize et
        print("\nİlan Borçluları tablosundaki tarihler normalize ediliyor...")
        borclular = session.query(IlanBorclu).all()
        borclu_guncelleme_sayisi = 0
        
        for borclu in borclular:
            guncellendi = False
            
            if borclu.karar_tarihi:
                normalized = normalize_tarih(borclu.karar_tarihi)
                if normalized != borclu.karar_tarihi:
                    print(f"  Borçlu {borclu.id}: karar_tarihi '{borclu.karar_tarihi}' -> '{normalized}'")
                    borclu.karar_tarihi = normalized
                    guncellendi = True
            
            if borclu.karar_baslangic_tarihi:
                normalized = normalize_tarih(borclu.karar_baslangic_tarihi)
                if normalized != borclu.karar_baslangic_tarihi:
                    print(f"  Borçlu {borclu.id}: karar_baslangic_tarihi '{borclu.karar_baslangic_tarihi}' -> '{normalized}'")
                    borclu.karar_baslangic_tarihi = normalized
                    guncellendi = True
            
            if borclu.durusma_tarihi:
                normalized = normalize_tarih(borclu.durusma_tarihi)
                if normalized != borclu.durusma_tarihi:
                    print(f"  Borçlu {borclu.id}: durusma_tarihi '{borclu.durusma_tarihi}' -> '{normalized}'")
                    borclu.durusma_tarihi = normalized
                    guncellendi = True
            
            if guncellendi:
                borclu_guncelleme_sayisi += 1
        
        # Değişiklikleri kaydet
        if ilan_guncelleme_sayisi > 0 or borclu_guncelleme_sayisi > 0:
            session.commit()
            print(f"\n[OK] Normalizasyon tamamlandi!")
            print(f"  - {ilan_guncelleme_sayisi} ilan guncellendi")
            print(f"  - {borclu_guncelleme_sayisi} borclu kaydi guncellendi")
        else:
            print("\n[OK] Tum tarihler zaten standart formatta!")
        
    except Exception as e:
        print(f"\n[HATA] Hata olustu: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("VERİTABANI TARİH NORMALİZASYONU")
    print("=" * 60)
    print("\nBu script mevcut veritabanındaki tarih formatlarını")
    print("standart formata (GG.AA.YYYY) çevirecektir.\n")
    
    onay = input("Devam etmek istiyor musunuz? (e/h): ").strip().lower()
    if onay == 'e':
        normalize_veritabani()
    else:
        print("İşlem iptal edildi.")

