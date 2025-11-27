#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanındaki "Oşuzhan" yazımlarını "Oğuzhan" olarak düzeltir.
"""

import pymysql

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

def fix_oguzhan_names():
    """Oşuzhan -> Oğuzhan düzeltmesi yapar"""
    print("=" * 60)
    print("Oşuzhan -> Oğuzhan Düzeltme İşlemi")
    print("=" * 60)
    print()
    
    try:
        # MySQL bağlantısı
        print("🔌 MySQL bağlantısı kuruluyor...")
        connection = pymysql.connect(**RAILWAY_CONFIG)
        print("✅ Bağlantı başarılı!")
        
        cursor = connection.cursor()
        
        # Önce bulunan kayıtları göster
        print("\n📊 Bulunan kayıtlar:")
        cursor.execute("""
            SELECT id, borclu_adi 
            FROM ilan_borclulari 
            WHERE borclu_adi LIKE '%Oşuzhan%' 
            OR borclu_adi LIKE '%OŞUZHAN%'
        """)
        borclular = cursor.fetchall()
        print(f"   İlan borçluları: {len(borclular)} kayıt")
        for row in borclular[:5]:  # İlk 5'ini göster
            print(f"   - ID {row[0]}: {row[1]}")
        
        cursor.execute("""
            SELECT id, full_name 
            FROM users 
            WHERE full_name LIKE '%Oşuzhan%' 
            OR full_name LIKE '%OŞUZHAN%'
        """)
        users = cursor.fetchall()
        print(f"   Kullanıcılar: {len(users)} kayıt")
        for row in users:
            print(f"   - ID {row[0]}: {row[1]}")
        
        cursor.execute("""
            SELECT id, metin 
            FROM ilanlar 
            WHERE metin LIKE '%Oşuzhan%' 
            OR metin LIKE '%OŞUZHAN%'
        """)
        ilanlar = cursor.fetchall()
        print(f"   İlanlar (metin içinde): {len(ilanlar)} kayıt")
        
        # Düzeltme işlemleri
        print("\n🔧 Düzeltme işlemleri başlıyor...")
        
        # 1. İlan borçluları tablosu
        cursor.execute("""
            UPDATE ilan_borclulari 
            SET borclu_adi = REPLACE(REPLACE(borclu_adi, 'Oşuzhan', 'Oğuzhan'), 'OŞUZHAN', 'OĞUZHAN')
            WHERE borclu_adi LIKE '%Oşuzhan%' OR borclu_adi LIKE '%OŞUZHAN%'
        """)
        affected_borclular = cursor.rowcount
        print(f"   ✓ İlan borçluları: {affected_borclular} kayıt düzeltildi")
        
        # 2. Users tablosu
        cursor.execute("""
            UPDATE users 
            SET full_name = REPLACE(REPLACE(full_name, 'Oşuzhan', 'Oğuzhan'), 'OŞUZHAN', 'OĞUZHAN')
            WHERE full_name LIKE '%Oşuzhan%' OR full_name LIKE '%OŞUZHAN%'
        """)
        affected_users = cursor.rowcount
        print(f"   ✓ Kullanıcılar: {affected_users} kayıt düzeltildi")
        
        # 3. İlanlar tablosu (metin içinde)
        cursor.execute("""
            UPDATE ilanlar 
            SET metin = REPLACE(REPLACE(metin, 'Oşuzhan', 'Oğuzhan'), 'OŞUZHAN', 'OĞUZHAN')
            WHERE metin LIKE '%Oşuzhan%' OR metin LIKE '%OŞUZHAN%'
        """)
        affected_ilanlar = cursor.rowcount
        print(f"   ✓ İlanlar: {affected_ilanlar} kayıt düzeltildi")
        
        # Değişiklikleri kaydet
        connection.commit()
        
        # Sonuçları kontrol et
        print("\n✅ Düzeltme tamamlandı!")
        print(f"\n📊 Toplam düzeltilen kayıt sayısı: {affected_borclular + affected_users + affected_ilanlar}")
        
        # Kontrol sorgusu
        print("\n🔍 Kontrol sorgusu:")
        cursor.execute("SELECT id, full_name FROM users WHERE id = 3")
        user = cursor.fetchone()
        if user:
            print(f"   User ID 3: {user[1]}")
        
        cursor.execute("SELECT id, borclu_adi FROM ilan_borclulari WHERE borclu_adi LIKE '%Oğuzhan%' LIMIT 3")
        borclular = cursor.fetchall()
        print(f"   Örnek borçlu kayıtları:")
        for row in borclular:
            print(f"   - ID {row[0]}: {row[1]}")
        
        cursor.close()
        connection.close()
        
        return 0
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(fix_oguzhan_names())




