# 🧪 Concordato Scraper Test Kılavuzu

## 📋 Ön Hazırlık

### 1. Veritabanı Kontrolü
MySQL'in çalıştığından ve `config.py` ayarlarının doğru olduğundan emin olun.

```bash
# MySQL'e bağlanabildiğinizi kontrol edin
mysql -u root -p -h localhost
```

---

## 🖥️ YÖNTEM 1: YEREL TEST (Önerilen İlk Test)

### Avantajları:
- ✅ Tarayıcı görünür (debug kolay)
- ✅ Loglar canlı terminalde
- ✅ Hızlı başlatma
- ✅ Kod değişikliği sonrası hemen test

### Adımlar:

#### 1. Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

#### 2. Chrome Tarayıcısının Yüklü Olduğunu Kontrol Edin
Sistem tarayıcınızın güncel olduğundan emin olun. Selenium otomatik olarak uygun driver'ı indirecek.

#### 3. Scraper'ı Çalıştırın
```bash
python main_scraper.py
```

#### 4. Test Senaryoları

**Test 1: Küçük Tarih Aralığı (Hızlı Test)**
```
Başlangıç Tarihi: 20.11.2025
Bitiş Tarihi: 21.11.2025
```
Beklenen: 1-2 sayfa, ~10-20 ilan

**Test 2: Tarih Filtresi Olmadan**
```
Başlangıç Tarihi: [Enter]
Bitiş Tarihi: [Enter]
```
Beklenen: Tüm ilanlar taranır (uzun sürebilir)

**Test 3: Aynı Aralığı İkinci Kez Çalıştırın**
```
Başlangıç Tarihi: 20.11.2025
Bitiş Tarihi: 21.11.2025
```
Beklenen: Tüm ilanlar "ATLANDI (Zaten var)" mesajı ile geçilmeli

### 5. Log Takibi
Loglar terminalde canlı görünür:
```
✓ Toplam 15 sayfa tespit edildi.
✓ 0 mevcut ilan önbellekte.

============================================================
SAYFA 1/15 İŞLENİYOR
============================================================
[Sayfa 1 - 1/12] İşleniyor... Link: ...
   ✓ Veriler toplandı: ILN123456
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sayfa 1 için 12 ilan veritabanına yazılıyor...
✓ 12 ilan başarıyla kaydedildi!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

### 6. Hata Durumları

**Hata: "Veritabanı Bağlantı Hatası"**
- `config.py` dosyasını kontrol edin
- MySQL servisinin çalıştığından emin olun

**Hata: "ChromeDriver hatası"**
- Chrome tarayıcınızın güncel olduğundan emin olun
- İnternet bağlantınızı kontrol edin (driver indirmek için)

---

## 🐳 YÖNTEM 2: DOCKER İLE TEST (Production Ortamı)

### Avantajları:
- ✅ İzole ortam
- ✅ Production'a yakın test
- ✅ Headless mode (arka planda çalışır)
- ✅ MySQL dahil tam paket

### Adımlar:

#### 1. Docker Container'ları Başlatın
```bash
# Container'ları build edin ve başlatın
docker-compose up --build -d
```

#### 2. Container'ların Çalıştığını Kontrol Edin
```bash
docker ps
```

Çıktı:
```
CONTAINER ID   IMAGE              STATUS         PORTS                    NAMES
xxx            concordato_app     Up 10 seconds  0.0.0.0:8501->8501/tcp  concordato_app
yyy            mysql:8.0          Up 10 seconds  0.0.0.0:3307->3306/tcp  concordato_db
```

#### 3. Scraper'ı Container İçinde Çalıştırın

**Seçenek A: Tarih Aralığı İle**
```bash
docker exec -it concordato_app python main_scraper.py
```
Not: Container'da input çalışmayabilir, environment variable kullanın:

```bash
docker exec -it -e BASLANGIC_TARIHI="20.11.2025" -e BITIS_TARIHI="21.11.2025" concordato_app python main_scraper.py
```

**Seçenek B: docker-compose ile Scheduled (Zamanlı Çalıştırma)**
`docker-compose.yml` dosyasına cron job ekleyin veya manuel çalıştırın.

#### 4. Logları İzleyin

**Canlı Log Takibi:**
```bash
# Tüm container logları
docker-compose logs -f app

# Sadece scraper çalıştırırken
docker exec -it concordato_app python main_scraper.py
```

**Geçmiş Loglar:**
```bash
# Son 100 satır
docker-compose logs --tail=100 app

# Belirli bir zamandan sonraki loglar
docker-compose logs --since 10m app
```

#### 5. Container İçine Girmek (Debug İçin)
```bash
docker exec -it concordato_app bash
```

Container içindeyken:
```bash
# Manuel test
python main_scraper.py

# Veritabanı bağlantısı testi
python check_data.py

# Çıkmak için
exit
```

---

## 📊 Test Sonrası Kontroller

### 1. Veritabanını Kontrol Edin

**Yerel MySQL:**
```bash
mysql -u root -p -h localhost ilan_db
```

**Docker MySQL:**
```bash
# Dışarıdan
mysql -u root -p -h localhost -P 3307 ilan_db

# Ya da container içinden
docker exec -it concordato_db mysql -u root -p ilan_db
```

**SQL Sorguları:**
```sql
-- Toplam ilan sayısı
SELECT COUNT(*) as toplam_ilan FROM ilanlar;

-- Son eklenen 10 ilan
SELECT ilan_no, baslik, sehir, eklenme_tarihi 
FROM ilanlar 
ORDER BY eklenme_tarihi DESC 
LIMIT 10;

-- Tarih aralığına göre ilanlar
SELECT ilan_no, yayin_tarihi, baslik 
FROM ilanlar 
WHERE yayin_tarihi LIKE '%21.11.2025%';

-- Duplicate kontrolü
SELECT ilan_no, COUNT(*) as adet 
FROM ilanlar 
GROUP BY ilan_no 
HAVING adet > 1;
```

### 2. Log Analizi Kontrol Noktaları

✅ **Başarılı Çalışma İşaretleri:**
- "✓ Toplam X sayfa tespit edildi"
- "✓ Y mevcut ilan önbellekte"
- "✓ Z ilan başarıyla kaydedildi!"
- "TARAMA TAMAMLANDI!"

⚠️ **Dikkat Edilmesi Gerekenler:**
- "ATLANDI (Zaten var)" - Normal (duplicate önleme)
- "⚠ Duplicate ilan tespit edildi" - Nadir görülür, önbellek senkronizasyon sorunu
- "! Sayfa X yüklenemedi" - Network veya timeout sorunu
- "✗ Veritabanı hatası" - DB bağlantı sorunu

---

## 🔧 Performans Testi

### Küçük Ölçekli Test (1-2 Sayfa)
```
Tarih: Son 1-2 gün
Beklenen Süre: 2-5 dakika
İlan Sayısı: 10-20
```

### Orta Ölçekli Test (5-10 Sayfa)
```
Tarih: Son 1 hafta
Beklenen Süre: 10-20 dakika
İlan Sayısı: 50-100
```

### Tam Tarama (Tüm İlanlar)
```
Tarih: Filtre yok
Beklenen Süre: 1-3 saat
İlan Sayısı: 1000+
```

---

## 🚨 Sorun Giderme

### Problem: Selenium Hatası
```bash
# ChromeDriver'ı manuel güncelle
pip install --upgrade webdriver-manager
```

### Problem: MySQL Bağlantı Hatası (Docker)
```bash
# DB container'ın hazır olduğundan emin olun
docker-compose logs db | grep "ready for connections"

# Container'ı yeniden başlatın
docker-compose restart db
```

### Problem: Yavaş Çalışma
- Görseller zaten devre dışı ✅
- Headless modda çalıştırın: `set HEADLESS=true`
- İnternet bağlantınızı kontrol edin

### Problem: Duplicate İlanlar
```sql
-- Duplicate'leri temizle (dikkatli kullanın!)
DELETE t1 FROM ilanlar t1
INNER JOIN ilanlar t2 
WHERE t1.id > t2.id 
AND t1.ilan_no = t2.ilan_no;
```

---

## 📈 İzleme ve Raporlama

### Basit İstatistik Raporu
```python
# check_data.py kullanarak
python check_data.py
```

### Streamlit Dashboard (Varsa)
```bash
streamlit run app.py
```
Tarayıcıda: http://localhost:8501

---

## ✅ Test Checklist

- [ ] Yerel ortamda başarılı çalıştı
- [ ] En az 10 ilan kaydedildi
- [ ] Aynı ilanlar ikinci çalıştırmada atlandı
- [ ] Veritabanında duplicate yok
- [ ] Loglar düzgün görünüyor
- [ ] Docker ortamında çalıştı (opsiyonel)
- [ ] Performans kabul edilebilir

---

## 📞 Sonuç

**Başarılı Test Çıktısı Örneği:**
```
============================================================
TARAMA TAMAMLANDI!
Toplam 15 sayfa tarandı.
170 yeni ilan veritabanına eklendi.
============================================================
```

Herhangi bir sorun olursa logları detaylı inceleyin ve hatayı rapor edin!

