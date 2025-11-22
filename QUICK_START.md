# ⚡ Hızlı Başlangıç Kılavuzu

## 🎯 5 Dakikada Test

### Yöntem 1: Yerel Test (En Hızlı)

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Çalıştır
python main_scraper.py

# 3. Test girdileri
Başlangıç Tarihi: 20.11.2025
Bitiş Tarihi: 21.11.2025
```

**Loglar**: Terminalde canlı görünür ✅

---

### Yöntem 2: Docker Test

```bash
# 1. Başlat
docker-compose up -d

# 2. 30 saniye bekle (MySQL hazır olsun)

# 3. Çalıştır
docker exec -it concordato_app python main_scraper.py

# 4. Logları izle
docker-compose logs -f app
```

**Loglar**: `docker-compose logs -f app` ile izleyin ✅

---

## 📋 Hızlı Kontrol Komutları

### Veritabanı Kontrolü
```bash
python check_data.py
```

### MySQL'e Bağlan (Yerel)
```bash
mysql -u root -p -h localhost ilan_db
```

### MySQL'e Bağlan (Docker)
```bash
mysql -u root -p -h localhost -P 3307 ilan_db
```

### Toplam İlan Sayısı (SQL)
```sql
SELECT COUNT(*) FROM ilanlar;
```

---

## 🔍 Log Örnekleri

### ✅ Başarılı Çalışma
```
✓ Toplam 15 sayfa tespit edildi.
✓ 0 mevcut ilan önbellekte.
[Sayfa 1 - 1/12] İşleniyor...
   ✓ Veriler toplandı: ILN123456
✓ 12 ilan başarıyla kaydedildi!
TARAMA TAMAMLANDI!
```

### ⚠️ Duplicate Bulundu (Normal)
```
[Sayfa 1 - 3/12] ATLANDI (Zaten var): ILN789012
   . Zaten mevcut.
```

### ❌ Hata Durumu
```
✗ Veritabanı hatası: Can't connect to MySQL server
! Sayfa 5 yüklenemedi, atlanıyor
```

---

## 🚀 Önerilen Test Sırası

1. **İlk Test** (2-3 dakika)
   - Tarih: Son 1 gün
   - Hedef: 10-20 ilan
   
2. **Duplicate Test** (1 dakika)
   - Aynı tarihi tekrar çalıştır
   - Hedef: Tüm ilanlar atlanmalı
   
3. **Büyük Test** (30+ dakika)
   - Tarih filtresi yok
   - Hedef: Tüm sistem testi

---

## 📞 Sorun mu var?

1. `config.py` kontrol et
2. MySQL servisini kontrol et
3. `TEST_KLAVUZU.md` dosyasına bak
4. Hata loglarını incele

