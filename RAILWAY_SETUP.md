# Railway Deployment Rehberi

Bu proje Railway'e deploy için hazırlanmıştır (scraper olmadan, sadece statik veri gösterimi).

## Gerekli Environment Variables

Railway dashboard'da aşağıdaki environment variable'ları ekle:

### Backend Servisi

```env
# Database (Railway MySQL Plugin'den alacaksın)
DB_HOST=your-mysql-host.railway.app
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=railway

# Redis (Railway Redis Plugin'den alacaksın)
REDIS_URL=redis://default:password@redis.railway.internal:6379

# CORS (Railway'in verdiği domain'leri ekle, virgülle ayır)
CORS_ALLOW_ORIGINS=https://your-frontend.railway.app,https://your-backend.railway.app

# JWT Secret (güvenli bir string oluştur - openssl rand -hex 32 ile)
SECRET_KEY=your-secret-key-here-change-this-in-production

# Optional
HEADLESS=true
```

## Deploy Adımları

### 1. Railway'de Proje Oluştur
- Railway dashboard'a git: https://railway.app
- "New Project" > "Deploy from GitHub repo"
- Bu repo'yu seç, **railway-deploy** branch'ini seç

### 2. MySQL Ekle
- "New" > "Database" > "Add MySQL"
- Otomatik env vars oluşacak (DATABASE_URL)
- Not: Railway'in verdiği değerleri yukarıdaki env vars'a kopyala

### 3. Redis Ekle
- "New" > "Database" > "Add Redis"
- Otomatik REDIS_URL oluşacak

### 4. Backend Servisi
- Railway otomatik `Dockerfile.railway`'i algılayacak
- Port: 8000
- Environment variables'ı yukarıdan ekle

### 5. Frontend Servisi (İsteğe Bağlı)
Frontend'i ayrı deploy etmek istersen:
- "New" > "Service" > GitHub repo > frontend klasörü
- Build Command: `npm install && npm run build`
- Start Command: `npm run preview`
- Port: 4173 (Vite preview default)

### 6. Database Migration
Yerel MySQL verilerini Railway'e aktar:

```bash
# 1. Yerel DB'yi export et
mysqldump -u root -p ilan_db > dump.sql

# 2. Railway MySQL'e bağlan (Railway'den connection string al)
mysql -h your-mysql-host.railway.app -u root -p railway < dump.sql
```

### 7. Test Et
- Railway backend URL'ini aç (örneğin: https://your-app.up.railway.app)
- API çalışıyor mu kontrol et: `https://your-app.up.railway.app/docs`

## Notlar
- Bu branch scraper içermiyor (Chrome/Selenium yok)
- Master branch'e dönmek için: `git checkout master`
- Railway Trial plan $5 kredi verir, bitince durur
- Statik veri gösterimi için yeterli olacaktır

