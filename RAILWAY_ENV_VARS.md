# Railway Environment Variables - Güncel Ayarlar

## Backend Servisi için Gerekli Environment Variables

Railway Dashboard > Backend Service > Variables sekmesine şunları ekle:

```env
# Database (Railway MySQL Plugin'den alacaksın)
MYSQL_URL=mysql://root:password@host:port/railway
# VEYA ayrı ayrı:
DB_HOST=your-mysql-host.railway.app
DB_USER=root
DB_PASSWORD=your-mysql-password-here
DB_NAME=railway

# Redis (Railway Redis Plugin'den alacaksın)
REDIS_URL=redis://default:password@redis.railway.internal:6379

# CORS - Netlify domain'ini ekle (virgülle ayır)
CORS_ALLOW_ORIGINS=https://your-app.netlify.app,https://concordato-app-production.up.railway.app

# Cookie Ayarları (Cross-domain için)
COOKIE_SECURE=true  # HTTPS için true (production)
COOKIE_SAMESITE=lax  # Cross-site için lax veya none
COOKIE_DOMAIN=  # Boş bırak (cross-domain için)

# JWT Secret (güvenli bir string - değiştir!)
SECRET_KEY=your-secret-key-here-change-this-in-production-min-32-chars

# Optional
HEADLESS=true
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Önemli Notlar

1. **CORS_ALLOW_ORIGINS**: Netlify domain'inizi ekleyin (örn: `https://concordato-app.netlify.app`)
2. **COOKIE_SECURE**: Production'da `true` olmalı (HTTPS için)
3. **COOKIE_DOMAIN**: Cross-domain için boş bırakın (None)
4. **SECRET_KEY**: Güvenli bir string kullanın (en az 32 karakter)

## Netlify Environment Variables

Netlify Dashboard > Site Settings > Environment Variables:

```env
VITE_API_URL=https://concordato-app-production.up.railway.app
```

## Test Etme

1. Railway'de backend servisinin deploy olduğunu kontrol et
2. Netlify'da frontend'in deploy olduğunu kontrol et
3. Netlify URL'inden giriş yapmayı dene
4. F12 > Network sekmesinde `/users/me` isteğini kontrol et
   - Authorization header'da token olmalı
   - 200 OK dönmeli




