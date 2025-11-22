#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import get_db_session, Ilan, IlanBorclu

session = get_db_session()

print("=" * 60)
print("VERİTABANI DURUM RAPORU")
print("=" * 60)

# İlan sayısı
ilan_count = session.query(Ilan).count()
print(f"\n📋 Toplam İlan Sayısı: {ilan_count}")

# Borçlu sayısı
borclu_count = session.query(IlanBorclu).count()
print(f"👤 Toplam Borçlu Kaydı: {borclu_count}")

# Analiz yapılmış ilan sayısı
analyzed_ilan_ids = session.query(IlanBorclu.ilan_id).distinct().all()
analyzed_count = len(analyzed_ilan_ids)
print(f"✅ Analiz Yapılmış İlan: {analyzed_count}")
print(f"⏳ Analiz Bekleyen İlan: {ilan_count - analyzed_count}")

# Son 3 ilanı ve borçlularını göster
print("\n" + "=" * 60)
print("SON 3 İLAN VE BORÇLULARI")
print("=" * 60)

recent_ilans = session.query(Ilan).order_by(Ilan.id.desc()).limit(3).all()

for ilan in recent_ilans:
    print(f"\n📄 İlan #{ilan.id}: {ilan.ilan_no}")
    print(f"   Başlık: {ilan.baslik[:60]}..." if len(ilan.baslik) > 60 else f"   Başlık: {ilan.baslik}")
    
    borclular = session.query(IlanBorclu).filter_by(ilan_id=ilan.id).all()
    if borclular:
        print(f"   👥 Borçlu Sayısı: {len(borclular)}")
        for idx, borclu in enumerate(borclular, 1):
            print(f"      {idx}. {borclu.borclu_adi} ({borclu.borclu_tipi})")
    else:
        print("   ⚠️  Borçlu kaydı yok (Analiz yapılmamış)")

print("\n" + "=" * 60)

session.close()

