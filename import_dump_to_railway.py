#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Düzeltilmiş dump dosyasını Railway MySQL'e import eder.
Encoding sorunlarını önlemek için Python kullanır.
"""

import pymysql
import sys
import re

# Railway MySQL bağlantı bilgileri
RAILWAY_CONFIG = {
    'host': 'hopper.proxy.rlwy.net',
    'port': 45292,
    'user': 'root',
    'password': 'qwlzRDsVGGVjDdoGvAveGynDYtpbyZKs',
    'database': 'railway',
    'charset': 'utf8mb4',
    'use_unicode': True
}

def execute_sql_file(cursor, sql_file):
    """SQL dosyasını satır satır okuyup çalıştırır."""
    print(f"📖 SQL dosyası okunuyor: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # SQL komutlarını ayır (; ile bitenler)
    # MySQL dump dosyalarında /*! */ yorumları var, bunları koru
    statements = []
    current_statement = ""
    
    # Basit bir parser - her satırı kontrol et
    for line in sql_content.split('\n'):
        # Yorum satırlarını atla (ama /*! */ içindekileri koru)
        if line.strip().startswith('--') and '/*!' not in line:
            continue
        
        current_statement += line + '\n'
        
        # Eğer satır ; ile bitiyorsa ve bir INSERT/DELETE/UPDATE/CREATE/DROP/ALTER ise
        if line.strip().endswith(';') and current_statement.strip():
            # Boş veya sadece yorum içeren statement'ları atla
            stmt = current_statement.strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_statement = ""
    
    # Son statement'ı ekle (eğer varsa)
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    print(f"✅ {len(statements)} SQL statement bulundu")
    print(f"🚀 Import başlıyor...")
    
    # Her statement'ı çalıştır
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements):
        try:
            # Çok uzun statement'ları atla (INSERT'ler çok uzun olabilir)
            if len(statement) > 1000000:  # 1MB'dan büyük
                print(f"   ⚠️  Statement {i+1} çok uzun, atlanıyor...")
                continue
            
            cursor.execute(statement)
            success_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"   ✓ {i+1}/{len(statements)} statement işlendi...")
                
        except Exception as e:
            error_count += 1
            # Sadece önemli hataları göster
            if 'Duplicate entry' not in str(e) and 'does not exist' not in str(e):
                print(f"   ❌ Hata (statement {i+1}): {str(e)[:100]}")
    
    print(f"\n✅ Import tamamlandı!")
    print(f"   - Başarılı: {success_count}")
    print(f"   - Hatalı: {error_count}")
    
    return success_count, error_count

def main():
    dump_file = 'dump_fixed.sql'
    
    print("=" * 60)
    print("Railway MySQL'e Dump Import")
    print("=" * 60)
    print()
    
    try:
        # MySQL bağlantısı
        print("🔌 MySQL bağlantısı kuruluyor...")
        connection = pymysql.connect(**RAILWAY_CONFIG)
        print("✅ Bağlantı başarılı!")
        
        cursor = connection.cursor()
        
        # Charset ayarlarını kontrol et
        cursor.execute("SET NAMES utf8mb4")
        cursor.execute("SET CHARACTER SET utf8mb4")
        cursor.execute("SET character_set_connection=utf8mb4")
        
        # Database charset kontrolü
        cursor.execute("SHOW VARIABLES LIKE 'character_set%'")
        print("\n📊 Charset ayarları:")
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]}")
        
        # Dump dosyasını import et
        print()
        success, errors = execute_sql_file(cursor, dump_file)
        
        # Değişiklikleri kaydet
        connection.commit()
        
        # Sonuçları kontrol et
        cursor.execute("SELECT COUNT(*) FROM ilan_borclulari")
        count = cursor.fetchone()[0]
        print(f"\n📊 İlan borçluları tablosunda {count} kayıt var")
        
        # Türkçe karakter kontrolü
        cursor.execute("SELECT mahkeme_adi FROM ilan_borclulari WHERE id=1")
        result = cursor.fetchone()
        if result:
            print(f"📝 Örnek veri (id=1): {result[0]}")
            if 'İstanbul' in result[0] or 'İSTANBUL' in result[0]:
                print("   ✅ Türkçe karakterler doğru görünüyor!")
            else:
                print("   ⚠️  Türkçe karakterler kontrol edilmeli")
        
        cursor.close()
        connection.close()
        
        return 0
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())




