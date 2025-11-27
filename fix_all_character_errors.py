#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanındaki tüm karakter hatalarını düzeltir.
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

# Karakter düzeltme mapping'i
CHAR_FIXES = [
    # ç -> ğ hataları
    ('ğok', 'çok'),
    ('borğlu', 'borçlu'),
    ('iğin', 'için'),
    ('deşişik', 'değişik'),
    ('ağılan', 'açılan'),
    ('komiserlişinden', 'komiserliğinden'),
    ('ğaşrı', 'çağrı'),
    ('hakimlişi', 'hakimliği'),
    ('müdürlüşü', 'müdürlüğü'),
    ('dilekğe', 'dilekçe'),
    ('hukukğu', 'hukukçu'),
    ('dolduşu', 'dolduğu'),
    ('olmadışının', 'olmadığının'),
    ('deşil', 'değil'),
    ('geğici', 'geçici'),
    ('m├╝hlet', 'mühlet'),
    ('M├╝HLET', 'MÜHLET'),
    ('M├╝hlet', 'Mühlet'),
    # Büyük harf versiyonları
    ('ĞOK', 'ÇOK'),
    ('BORĞLU', 'BORÇLU'),
    ('İĞİN', 'İÇİN'),
    ('DEŞİŞİK', 'DEĞİŞİK'),
    ('AĞILAN', 'AÇILAN'),
    ('KOMİSERLİŞİNDEN', 'KOMİSERLİĞİNDEN'),
    ('ĞAŞRI', 'ÇAĞRI'),
    ('HAKİMLİŞİ', 'HAKİMLİĞİ'),
    ('MÜDÜRLÜŞÜ', 'MÜDÜRLÜĞÜ'),
    ('DİLEKĞE', 'DİLEKÇE'),
    ('HUKUKĞU', 'HUKUKÇU'),
    ('DOLDUŞU', 'DOLDUĞU'),
    ('OLMADIŞININ', 'OLMADIĞININ'),
    ('DEŞİL', 'DEĞİL'),
    ('GEĞİCİ', 'GEÇİCİ'),
]

def fix_all_character_errors():
    """Tüm karakter hatalarını düzeltir"""
    print("=" * 60)
    print("Karakter Hataları Düzeltme İşlemi")
    print("=" * 60)
    print()
    
    try:
        # MySQL bağlantısı
        print("🔌 MySQL bağlantısı kuruluyor...")
        connection = pymysql.connect(**RAILWAY_CONFIG)
        print("✅ Bağlantı başarılı!")
        
        cursor = connection.cursor()
        
        total_fixed = 0
        
        # Her tablo için düzeltme yap
        tables_to_fix = [
            ('hata_raporlari', ['aciklama']),
            ('ilan_borclulari', ['borclu_adi', 'adres', 'karar_ozeti', 'mahkeme_adi']),
            ('ilanlar', ['baslik', 'metin']),
            ('users', ['full_name']),
        ]
        
        for table_name, columns in tables_to_fix:
            print(f"\n📋 {table_name} tablosu düzeltiliyor...")
            
            for column in columns:
                # Her karakter hatası için REPLACE yap
                for wrong, correct in CHAR_FIXES:
                    query = f"""
                        UPDATE {table_name} 
                        SET {column} = REPLACE({column}, %s, %s)
                        WHERE {column} LIKE %s
                    """
                    pattern = f'%{wrong}%'
                    cursor.execute(query, (wrong, correct, pattern))
                    affected = cursor.rowcount
                    if affected > 0:
                        print(f"   ✓ {column}: '{wrong}' -> '{correct}' ({affected} kayıt)")
                        total_fixed += affected
        
        # Değişiklikleri kaydet
        connection.commit()
        
        print(f"\n✅ Düzeltme tamamlandı!")
        print(f"📊 Toplam düzeltilen kayıt sayısı: {total_fixed}")
        
        # Kontrol sorgusu - hata raporları
        print("\n🔍 Kontrol sorgusu (hata_raporlari):")
        cursor.execute("SELECT id, aciklama FROM hata_raporlari WHERE id = 4")
        rapor = cursor.fetchone()
        if rapor:
            print(f"   ID {rapor[0]}: {rapor[1]}")
        
        # Kontrol sorgusu - ilanlar
        print("\n🔍 Kontrol sorgusu (ilanlar - geçici mühlet):")
        cursor.execute("SELECT id, baslik FROM ilanlar WHERE baslik LIKE '%geçici mühlet%' LIMIT 3")
        ilanlar = cursor.fetchall()
        for row in ilanlar:
            print(f"   ID {row[0]}: {row[1]}")
        
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
    sys.exit(fix_all_character_errors())




