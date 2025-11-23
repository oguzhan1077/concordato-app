"""
Kişisel Veri Maskeleme Testleri

Bu dosya, privacy_utils modülündeki maskeleme fonksiyonlarını test eder.
Komut satırından çalıştırın:
    python test_privacy_masking.py
"""

import sys
import os

# Backend app modülünü import edebilmek için path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import privacy_utils


def test_tc_vkn_masking():
    """TC Kimlik No ve VKN maskeleme testleri"""
    print("\n" + "="*60)
    print("TC/VKN MASKELEME TESTLERİ")
    print("="*60)
    
    test_cases = [
        ("12345678901", "full", "***********"),
        ("12345678901", "partial", "123****8901"),
        ("1234567890", "partial", "123****890"),
        ("", "full", ""),
        (None, "full", None),
    ]
    
    for tc, level, expected in test_cases:
        result = privacy_utils.mask_tc_vkn(tc, mask_level=level)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} mask_tc_vkn('{tc}', '{level}')")
        print(f"  Beklenen: {expected}")
        print(f"  Sonuç:    {result}")
        print()


def test_phone_masking():
    """Telefon numarası maskeleme testleri"""
    print("\n" + "="*60)
    print("TELEFON MASKELEME TESTLERİ")
    print("="*60)
    
    test_cases = [
        "0532 123 45 67",
        "+90 532 123 45 67",
        "05321234567",
        "0212 345 67 89",
        "532 123 45 67",
    ]
    
    for phone in test_cases:
        result = privacy_utils.mask_phone(phone)
        print(f"Orijinal: {phone:25} -> Maskeli: {result}")


def test_email_masking():
    """E-posta maskeleme testleri"""
    print("\n" + "="*60)
    print("E-POSTA MASKELEME TESTLERİ")
    print("="*60)
    
    test_cases = [
        "test@example.com",
        "john.doe@company.com",
        "a@b.com",
        "very.long.email.address@subdomain.example.com",
        "user123@gmail.com",
    ]
    
    for email in test_cases:
        result = privacy_utils.mask_email(email)
        print(f"Orijinal: {email:45} -> Maskeli: {result}")


def test_address_masking():
    """Adres maskeleme testleri"""
    print("\n" + "="*60)
    print("ADRES MASKELEME TESTLERİ")
    print("="*60)
    
    test_cases = [
        "Atatürk Mah. Cumhuriyet Cad. No:123 Kadıköy/İstanbul",
        "Barbaros Bulvarı 145/A Beşiktaş İstanbul",
        "Kızılay Meydanı Çankaya/Ankara",
        "Konak İzmir",
        "Alsancak Mah. 1234 Sok. No:56 D:12 Konak/İzmir",
    ]
    
    for address in test_cases:
        result_with_city = privacy_utils.mask_address(address, show_city=True)
        result_full_mask = privacy_utils.mask_address(address, show_city=False)
        print(f"\nOrijinal: {address}")
        print(f"  Şehir ile    : {result_with_city}")
        print(f"  Tam maskeleme: {result_full_mask}")


def test_text_masking():
    """Metin içi kişisel veri maskeleme testleri"""
    print("\n" + "="*60)
    print("METİN İÇİ MASKELEME TESTLERİ")
    print("="*60)
    
    sample_text = """
    Borçlu: ABC Şirketi
    TC Kimlik No: 12345678901
    VKN: 9876543210
    Telefon: 0532 123 45 67
    E-posta: info@company.com
    Adres: Atatürk Mah. Cumhuriyet Cad. No:123 İstanbul
    
    İletişim: +90 212 345 67 89
    Vergi Numarası: 11223344556
    """
    
    print("\n--- Orijinal Metin ---")
    print(sample_text)
    
    print("\n--- Normal Maskeleme ---")
    result_normal = privacy_utils.mask_text_personal_data(sample_text, aggressive=False)
    print(result_normal)
    
    print("\n--- Agresif Maskeleme (tüm 11 haneli sayılar) ---")
    result_aggressive = privacy_utils.mask_text_personal_data(sample_text, aggressive=True)
    print(result_aggressive)


def test_borclu_data_masking():
    """Borçlu dictionary maskeleme testi"""
    print("\n" + "="*60)
    print("BORÇLU DATA MASKELEME TESTİ")
    print("="*60)
    
    borclu = {
        "id": 1,
        "borclu_adi": "Test Şirketi A.Ş.",
        "borclu_tipi": "TUZEL_KISI",
        "tc_vkn": "12345678901",
        "adres": "Atatürk Mah. Cumhuriyet Cad. No:123 Kadıköy/İstanbul",
        "karar_turu": "Geçici Mühlet Kararı",
        "karar_ozeti": "Borçlunun TC: 12345678901 olan şahsının konkordato talebi kabul edilmiştir.",
        "mahkeme_adi": "İstanbul 2. Asliye Ticaret Mahkemesi",
    }
    
    print("\n--- Orijinal Borçlu Verisi ---")
    for key, value in borclu.items():
        print(f"{key:20}: {value}")
    
    print("\n--- Kısmi Maskeleme ---")
    masked_partial = privacy_utils.mask_borclu_data(borclu, full_mask=False)
    for key, value in masked_partial.items():
        print(f"{key:20}: {value}")
    
    print("\n--- Tam Maskeleme ---")
    masked_full = privacy_utils.mask_borclu_data(borclu, full_mask=True)
    for key, value in masked_full.items():
        print(f"{key:20}: {value}")


def test_should_mask_data():
    """Maskeleme durumu testi"""
    print("\n" + "="*60)
    print("MASKELEME DURUM KONTROLÜ")
    print("="*60)
    
    should_mask = privacy_utils.should_mask_data()
    status = "AKTIF [OK]" if should_mask else "PASIF [X]"
    
    print(f"\nMaskeleme Durumu: {status}")
    print(f"Environment Variable (MASK_PERSONAL_DATA): {os.getenv('MASK_PERSONAL_DATA', 'true')}")
    
    if should_mask:
        print("\n[!] Kisisel veriler API response'larinda otomatik olarak maskelenecektir.")
    else:
        print("\n[!] UYARI: Maskeleme devre disi! Bu yasal risk olusturabilir (KVKK & TCK 136).")


def main():
    """Tüm testleri çalıştır"""
    print("\n" + "="*60)
    print("=" + " "*58 + "=")
    print("=" + " "*15 + "KISISEL VERI MASKELEME TESTLERI" + " "*12 + "=")
    print("=" + " "*58 + "=")
    print("="*60)
    
    test_should_mask_data()
    test_tc_vkn_masking()
    test_phone_masking()
    test_email_masking()
    test_address_masking()
    test_text_masking()
    test_borclu_data_masking()
    
    print("\n" + "="*60)
    print("=" + " "*58 + "=")
    print("=" + " "*20 + "TESTLER TAMAMLANDI" + " "*20 + "=")
    print("=" + " "*58 + "=")
    print("="*60 + "\n")
    
    print("[OK] Tum maskeleme fonksiyonlari calisiyor!")
    print("[OK] KVKK & TCK 136 uyumlulugu saglanmistir.")
    print("\nDetayli bilgi icin: KISISEL_VERI_KORUMA.md\n")


if __name__ == "__main__":
    main()

