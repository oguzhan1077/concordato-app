# 🚀 Railway Deploy - Hızlı Başlangıç

Bu branch (`railway-deploy`) Railway'e deneme amaçlı deploy için hazırlanmıştır.

## ⚡ Hızlı Deploy (15-30 dakika)

### Adım 1: GitHub'a Push
```bash
# Değişiklikleri commit et
git add .
git commit -m "Railway deploy hazırlığı"

# GitHub'a push et
git push origin railway-deploy
```

### Adım 2: Railway'de Backend Servisi Oluştur

1. **Railway dashboard'a git**: https://railway.app/new
2. **"Deploy from GitHub repo"** seç
3. Repo'nu seç, **branch: railway-deploy** seçeneğini işaretle
4. **"Add variables"** ile aşağıdaki env vars'ı ekle:

```env
PORT=8000
```

### Adım 3: MySQL ve Redis Ekle

1. Aynı Railway projesinde **"New" > "Database" > "MySQL"** ekle
2. MySQL'den şu bilgileri kopyala (Variables sekmesinden):
   - MYSQL_HOST
   - MYSQL_USER
   - MYSQL_PASSWORD
   - MYSQL_DATABASE

3. Backend servisine dön, Variables'a ekle:
```env
DB_HOST=<MYSQL_HOST değeri>
DB_USER=<MYSQL_USER değeri>
DB_PASSWORD=<MYSQL_PASSWORD değeri>
DB_NAME=<MYSQL_DATABASE değeri>
```

4. **"New" > "Database" > "Redis"** ekle
5. Redis'ten REDIS_URL'i kopyala, backend'e ekle:
```env
REDIS_URL=<Redis'ten kopyala>
```

### Adım 4: CORS ve Secret Ayarla

Backend Variables'a ekle:
```env
CORS_ALLOW_ORIGINS=*
SECRET_KEY=<güvenli-bir-string-buraya-32-karakter>
```

Secret key oluşturmak için (PowerShell):
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### Adım 5: Deploy Et

Railway otomatik deploy başlatacak. 3-5 dakika içinde backend hazır olur.

### Adım 6: Database Migration (Opsiyonel)

Eğer yerel DB'nden veri aktarmak istersen:

```bash
# Yerel DB'yi export et
mysqldump -u root -p ilan_db > dump.sql

# Railway MySQL'e bağlan ve import et (Railway'den connection string kullan)
mysql -h <MYSQL_HOST> -u <MYSQL_USER> -p<MYSQL_PASSWORD> <MYSQL_DATABASE> < dump.sql
```

### Adım 7: Test Et

Railway backend URL'ini aç (Settings > Domains):
- Ana sayfa: `https://your-app.up.railway.app`
- API Docs: `https://your-app.up.railway.app/docs`

---

## 🎨 Frontend Deploy (Opsiyonel - 2 Seçenek)

### Seçenek A: Netlify'da Frontend (ÖNERİLEN)

1. Netlify'de yeni site oluştur
2. GitHub repo'sunu bağla, branch: `railway-deploy`
3. Build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
4. Environment variable ekle:
   ```
   VITE_API_URL=https://your-backend.up.railway.app
   ```
5. Deploy et

Frontend'te API URL'i güncellemen gerekir. `frontend/src` altındaki tüm dosyalarda:
```javascript
// Şu anki:
const API_URL = '/api';

// Railway backend için değiştir:
const API_URL = import.meta.env.VITE_API_URL || '/api';
```

### Seçenek B: Railway'de Ayrı Frontend Servisi

1. Railway projesinde **"New" > "Service"**
2. Aynı GitHub repo, branch: `railway-deploy`
3. Root directory: `frontend`
4. Environment variables:
   ```env
   VITE_API_URL=https://your-backend.up.railway.app
   PORT=4173
   ```
5. `railway.frontend.json` dosyasını `railway.json` olarak frontend klasörüne kopyala

---

## 📝 Notlar

- **Bu branch scraper içermez** (Chrome/Selenium yok) - daha hafif ve hızlı
- **Master branch'e dönmek için**: `git checkout master`
- **Railway Trial**: $5 kredi verir, düşük kullanımda 1-2 ay yeter
- **Maliyet**: Statik veri gösterimi için aylık $0-2 civarı (Hobby plan)

## 🔧 Sorun Giderme

**Deploy başarısız olursa:**
- Railway logs'u kontrol et (Dashboard > Deployments > View Logs)
- Environment variables eksik olabilir

**Database bağlantısı hata verirse:**
- MySQL servisinin UP olduğunu kontrol et
- DB_HOST, DB_USER vs. doğru kopyalandığını kontrol et

**CORS hatası alırsan:**
- Backend'de CORS_ALLOW_ORIGINS'e frontend URL'ini ekle
- Örnek: `CORS_ALLOW_ORIGINS=https://your-frontend.netlify.app`

## 🔙 Geri Dönmek İçin

```bash
git checkout master
```

Master branch'iniz değişmedi, orijinal Docker setup'ınız aynen duruyor.

---

**Yardıma ihtiyacın olursa detaylı rehber: [RAILWAY_SETUP.md](RAILWAY_SETUP.md)**

