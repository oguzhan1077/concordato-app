@echo off
REM Railway'e dump import scripti
REM Kullanım: import_to_railway.bat

echo ========================================
echo Railway MySQL'e Dump Import
echo ========================================
echo.

REM Railway MySQL bağlantı bilgileri
set RAILWAY_HOST=hopper.proxy.rlwy.net
set RAILWAY_PORT=45292
set RAILWAY_USER=root
set RAILWAY_PASSWORD=qwlzRDsVGGVjDdoGvAveGynDYtpbyZKs
set RAILWAY_DATABASE=railway
set DUMP_FILE=dump_fixed.sql

echo [1/3] Dump dosyası kontrol ediliyor...
if not exist "%DUMP_FILE%" (
    echo HATA: %DUMP_FILE% dosyası bulunamadı!
    echo Lütfen önce fix_dump_encoding.py scriptini çalıştırın.
    pause
    exit /b 1
)

echo [2/3] MySQL bağlantısı test ediliyor...
mysql -h %RAILWAY_HOST% -P %RAILWAY_PORT% -u %RAILWAY_USER% -p%RAILWAY_PASSWORD% -e "SELECT 1;" %RAILWAY_DATABASE% >nul 2>&1
if errorlevel 1 (
    echo HATA: MySQL bağlantısı başarısız!
    echo Lütfen Railway bilgilerini kontrol edin.
    pause
    exit /b 1
)

echo [3/3] Dump import ediliyor (bu biraz zaman alabilir)...
mysql -h %RAILWAY_HOST% -P %RAILWAY_PORT% -u %RAILWAY_USER% -p%RAILWAY_PASSWORD% --default-character-set=utf8mb4 %RAILWAY_DATABASE% < %DUMP_FILE%

if errorlevel 1 (
    echo.
    echo HATA: Import başarısız oldu!
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo Import başarılı!
    echo ========================================
    echo.
    echo Verileri kontrol etmek için Railway dashboard'u kullanabilirsiniz.
)

pause




