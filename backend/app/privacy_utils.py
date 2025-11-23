"""
Kişisel Verilerin Korunması (KVKK) ve TCK 136 uyarınca
kişisel verilerin maskelenmesi için yardımcı fonksiyonlar.

Bu modül, T.C. Kimlik No, VKN, telefon numarası, email ve adres 
gibi kişisel verileri maskeler.
"""

import re
from typing import Optional


def mask_tc_vkn(tc_vkn: Optional[str], mask_level: str = "full") -> Optional[str]:
    """
    TC Kimlik No veya VKN'yi maskeler.
    
    Args:
        tc_vkn: TC Kimlik No veya VKN (11 haneli)
        mask_level: "full" (tam maskeleme) veya "partial" (kısmi maskeleme)
        
    Returns:
        Maskelenmiş değer
        
    Örnekler:
        full: 12345678901 -> ***********
        partial: 12345678901 -> 123****8901
    """
    if not tc_vkn:
        return tc_vkn
    
    # Sadece rakamları al
    digits = re.sub(r'\D', '', str(tc_vkn))
    
    if not digits:
        return tc_vkn
    
    if mask_level == "full":
        # Tam maskeleme - tüm rakamları gizle
        return "*" * len(digits)
    elif mask_level == "partial":
        # Kısmi maskeleme - ilk 3 ve son 4 haneyi göster
        if len(digits) >= 11:
            return f"{digits[:3]}****{digits[-4:]}"
        elif len(digits) >= 7:
            return f"{digits[:2]}***{digits[-2:]}"
        else:
            return "*" * len(digits)
    
    return tc_vkn


def mask_phone(phone: Optional[str]) -> Optional[str]:
    """
    Telefon numarasını maskeler.
    
    Args:
        phone: Telefon numarası
        
    Returns:
        Maskelenmiş telefon
        
    Örnek:
        0532 123 45 67 -> 0532 *** ** **
        +90 532 123 45 67 -> +90 532 *** ** **
    """
    if not phone:
        return phone
    
    phone_str = str(phone)
    
    # Telefon numarası pattern'lerini maskele
    # Türkiye cep telefonu formatları
    patterns = [
        # +90 ile başlayanlar
        (r'(\+90\s*\d{3})\s*(\d{3})\s*(\d{2})\s*(\d{2})', r'\1 *** ** **'),  # +90 532 123 45 67
        
        # 0 ile başlayanlar
        (r'(0\d{3})\s*(\d{3})\s*(\d{2})\s*(\d{2})', r'\1 *** ** **'),  # 0532 123 45 67
        (r'(05\d{2})(\d{7})', r'\1*******'),  # 05321234567
        
        # 0 olmadan 5XX ile başlayanlar
        (r'\b(5\d{2})\s*(\d{3})\s*(\d{2})\s*(\d{2})\b', r'\1 *** ** **'),  # 532 123 45 67
        (r'\b(5\d{2})(\d{7})\b', r'\1*******'),  # 5367894352
        (r'\b(5\d{2})\s*(\d{3})\s*(\d{4})\b', r'\1 *** ****'),  # 532 123 4567
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, phone_str):
            return re.sub(pattern, replacement, phone_str)
    
    # Genel numara maskeleme - en az 7 haneli sayılar
    if re.search(r'\d{7,}', phone_str):
        # İlk 4 haneyi göster, geri kalanı maskele
        digits = re.findall(r'\d+', phone_str)[0]
        if len(digits) >= 7:
            masked_digits = digits[:4] + '*' * (len(digits) - 4)
            return phone_str.replace(digits, masked_digits)
    
    return phone_str


def mask_email(email: Optional[str]) -> Optional[str]:
    """
    Email adresini maskeler.
    
    Args:
        email: Email adresi
        
    Returns:
        Maskelenmiş email
        
    Örnek:
        test@example.com -> t***@example.com
        john.doe@company.com -> j*******@company.com
    """
    if not email:
        return email
    
    email_str = str(email).strip()
    
    # Email pattern kontrolü
    email_pattern = r'^([^@]+)@(.+)$'
    match = re.match(email_pattern, email_str)
    
    if match:
        username, domain = match.groups()
        
        if len(username) <= 1:
            masked_username = '*'
        elif len(username) <= 3:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            # İlk harfi göster, geri kalanı maskele
            masked_username = username[0] + '*' * (len(username) - 1)
        
        return f"{masked_username}@{domain}"
    
    return email_str


def mask_address(address: Optional[str], show_city: bool = True) -> Optional[str]:
    """
    Adres bilgisini maskeler.
    
    Args:
        address: Adres metni
        show_city: Şehir/İl bilgisini göster
        
    Returns:
        Maskelenmiş adres
        
    Örnek:
        "Atatürk Mah. Cumhuriyet Cad. No:123 Kadıköy/İstanbul" 
        -> "********** İstanbul"
    """
    if not address:
        return address
    
    address_str = str(address).strip()
    
    if not show_city:
        # Tamamen maskele
        return "****** [Gizli Adres] ******"
    
    # Türkiye şehirleri listesi (en yaygın olanlar)
    turkish_cities = [
        'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya',
        'Gaziantep', 'Şanlıurfa', 'Kocaeli', 'Mersin', 'Diyarbakır', 'Hatay',
        'Manisa', 'Kayseri', 'Samsun', 'Balıkesir', 'Kahramanmaraş', 'Van',
        'Aydın', 'Denizli', 'Sakarya', 'Tekirdağ', 'Muğla', 'Eskişehir',
        'Mardin', 'Malatya', 'Erzurum', 'Trabzon', 'Elazığ', 'Sivas',
        'Adıyaman', 'Osmaniye', 'Kırıkkale', 'Afyonkarahisar', 'Aksaray',
        'Amasya', 'Artvin', 'Bartın', 'Batman', 'Bayburt', 'Bilecik',
        'Bingöl', 'Bitlis', 'Bolu', 'Burdur', 'Çanakkale', 'Çankırı',
        'Çorum', 'Düzce', 'Edirne', 'Giresun', 'Gümüşhane', 'Hakkari',
        'Iğdır', 'Isparta', 'Karabük', 'Karaman', 'Kars', 'Kastamonu',
        'Kilis', 'Kırklareli', 'Kırşehir', 'Kütahya', 'Muş', 'Nevşehir',
        'Niğde', 'Ordu', 'Rize', 'Şırnak', 'Sinop', 'Tokat', 'Tunceli',
        'Uşak', 'Yalova', 'Yozgat', 'Zonguldak', 'Ardahan', 'Ağrı'
    ]
    
    # Şehir adını bul
    found_city = None
    for city in turkish_cities:
        if city.upper() in address_str.upper():
            found_city = city
            break
    
    if found_city:
        return f"****** {found_city}"
    else:
        # Şehir bulunamadıysa, adresin son kelimesini al (genelde şehir olur)
        words = address_str.split()
        if len(words) > 1:
            # Son 1-2 kelimeyi göster (şehir/ilçe olabilir)
            visible_part = " ".join(words[-2:]) if len(words) >= 2 else words[-1]
            return f"****** {visible_part}"
        else:
            return "****** [Gizli Adres]"


def mask_address_in_text(address_text: str) -> str:
    """
    Metin içindeki adres ifadesini maskeler.
    Şehir adını korur, geri kalanı gizler.
    
    Args:
        address_text: Adres içeren metin
        
    Returns:
        Maskelenmiş adres (şehir görünür)
        
    Örnekler:
        "Yahyalar Mah. Eski Hendek Cad No:50/2 Adapazarı SAKARYA"
        -> "****** SAKARYA"
        
        "SON YERLEŞİM YERİ: Atatürk Mah. İstanbul"
        -> "SON YERLEŞİM YERİ: ****** İstanbul"
    """
    # Türkiye şehirleri listesi (tüm 81 il)
    turkish_cities = [
        'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya',
        'Gaziantep', 'Şanlıurfa', 'Kocaeli', 'Mersin', 'Diyarbakır', 'Hatay',
        'Manisa', 'Kayseri', 'Samsun', 'Balıkesir', 'Kahramanmaraş', 'Van',
        'Aydın', 'Denizli', 'Sakarya', 'Tekirdağ', 'Muğla', 'Eskişehir',
        'Mardin', 'Malatya', 'Erzurum', 'Trabzon', 'Elazığ', 'Sivas',
        'Adıyaman', 'Osmaniye', 'Kırıkkale', 'Afyonkarahisar', 'Aksaray',
        'Amasya', 'Artvin', 'Bartın', 'Batman', 'Bayburt', 'Bilecik',
        'Bingöl', 'Bitlis', 'Bolu', 'Burdur', 'Çanakkale', 'Çankırı',
        'Çorum', 'Düzce', 'Edirne', 'Giresun', 'Gümüşhane', 'Hakkari',
        'Iğdır', 'Isparta', 'Karabük', 'Karaman', 'Kars', 'Kastamonu',
        'Kilis', 'Kırklareli', 'Kırşehir', 'Kütahya', 'Muş', 'Nevşehir',
        'Niğde', 'Ordu', 'Rize', 'Şırnak', 'Sinop', 'Tokat', 'Tunceli',
        'Uşak', 'Yalova', 'Yozgat', 'Zonguldak', 'Ardahan', 'Ağrı'
    ]
    
    # Şehir adını bul (Türkçe karakter duyarsız)
    found_city = None
    
    # Türkçe karakterleri normalize et
    def normalize_turkish(text):
        replacements = {
            'İ': 'I', 'ı': 'i', 'Ğ': 'G', 'ğ': 'g',
            'Ü': 'U', 'ü': 'u', 'Ş': 'S', 'ş': 's',
            'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
        }
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        return text.upper()
    
    normalized_address = normalize_turkish(address_text)
    
    for city in turkish_cities:
        normalized_city = normalize_turkish(city)
        if normalized_city in normalized_address:
            found_city = city
            break
    
    # Etiket kontrolü (örn: "SON YERLEŞİM YERİ:", "ADRES:", "İKAMETGAH:")
    label_match = re.match(r'^([A-ZÇĞİÖŞÜa-zçğıöşü\s:]+:)\s*', address_text)
    
    if found_city:
        if label_match:
            label = label_match.group(1)
            return f"{label} ****** {found_city}"
        else:
            return f"****** {found_city}"
    else:
        # Şehir bulunamadıysa tamamen maskele
        if label_match:
            label = label_match.group(1)
            return f"{label} ****** [Gizli Adres]"
        else:
            return "****** [Gizli Adres]"


def mask_text_personal_data(text: Optional[str], aggressive: bool = False) -> Optional[str]:
    """
    Serbest metindeki kişisel verileri otomatik olarak maskeler.
    
    Bu fonksiyon, metin içindeki TC Kimlik No, telefon numarası, 
    email gibi pattern'leri tespit eder ve maskeler.
    
    Args:
        text: Maskelenecek metin
        aggressive: True ise daha agresif maskeleme (11 haneli tüm sayılar)
        
    Returns:
        Maskelenmiş metin
    """
    if not text:
        return text
    
    masked_text = str(text)
    
    # 1. Email adreslerini maskele
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, masked_text)
    for email in emails:
        masked_text = masked_text.replace(email, mask_email(email))
    
    # 2. Telefon numaralarını maskele
    # Türk telefon formatları
    phone_patterns = [
        # +90 ile başlayanlar
        r'\+?90[\s\-]?5\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',  # +90 532 123 45 67
        
        # 0 ile başlayanlar
        r'0\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',  # 0532 123 45 67
        r'0\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',  # 0532 1234567
        
        # 0 olmadan 5XX ile başlayanlar (cep telefonu formatları)
        r'\b5\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b',  # 532 123 45 67
        r'\b5\d{9}\b',  # 5367894352 (10 haneli bitişik)
        r'\b5\d{2}[\s\-]?\d{3}[\s\-]?\d{4}\b',  # 532 123 4567
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, masked_text)
        for phone in phones:
            masked_text = masked_text.replace(phone, mask_phone(phone))
    
    # 3. TC Kimlik No / VKN (11 haneli sayılar)
    if aggressive:
        # Agresif mod: Tüm 11 haneli sayıları maskele
        # Önce word boundary ile dene (normal durumlar için)
        tc_pattern = r'\b\d{11}\b'
        masked_text = re.sub(tc_pattern, '***********', masked_text)
        
        # Sonra word boundary olmadan da dene (bitişik yazılanlar için)
        # Örn: "40048486206en" gibi durumlarda
        tc_pattern_relaxed = r'(?<!\d)(\d{11})(?!\d)'
        masked_text = re.sub(tc_pattern_relaxed, '***********', masked_text)
    else:
        # Normal mod: Sadece TC/VKN bağlamında geçenleri maskele
        # "TC:", "T.C.:", "VKN:", "Vergi No:" gibi etiketlerden sonra gelen 11 haneli sayılar
        tc_labeled_pattern = r'(T\.?C\.?\s*(?:Kimlik\s*)?(?:No|Numarası)?[\s:]*|VKN[\s:]*|Vergi\s*(?:Kimlik\s*)?(?:No|Numarası)?[\s:]*)(\d{11})'
        masked_text = re.sub(tc_labeled_pattern, r'\1***********', masked_text)
    
    # 4. Adres bilgilerini maskele
    # Türkiye'deki yaygın adres pattern'lerini tespit et
    address_patterns = [
        # "Mahalle" içeren ifadeler (örn: "Yahyalar Mah. Eski Hendek Cad...")
        r'([A-ZÇĞİÖŞÜa-zçğıöşü0-9\s]+Mah(?:allesi)?\.?\s+[^.\n]{10,100})',
        
        # "Cadde/Sokak/Bulvar" içeren ifadeler (örn: "Cumhuriyet Cad No:123")
        r'([A-ZÇĞİÖŞÜa-zçğıöşü\s]+(?:Cad|Sok|Bulvarı|Bulvar|Cd|Sk)\.?\s+(?:No[:.\s]*\d+)?[^.\n]{0,50})',
        
        # Etiketli adresler (örn: "SON YERLEŞİM YERİ: ...", "ADRES: ...", "İKAMETGAH: ...")
        r'((?:SON\s+)?(?:YERLEŞİM\s+)?(?:YER[İI]|ADRES|İKAMETGAH|KAYITLI\s+ADRES)[:\s]+[^\n]{10,150})',
        
        # "İkamet adresi" gibi ifadeler
        r'((?:İKAMET|İŞ|EV)\s+(?:ADRES[İI]|YER[İI])[:\s]+[^\n]{10,150})',
        
        # "ikametgahı" (tek kelime) formatı - Türkçe iyelik eki ile
        r'((?:son\s+)?ikametgah[ıi]\s*[:]+\s*[^\n]{5,150})',
        
        # Adres devamı: "NO: 104İÇ KAPI NO: 1 ..." ve ilçe/şehir içerenler
        r'(\.?\s*(?:NO|NUMARA)[:.\s]*\d+[^.\n]{10,150})',
    ]
    
    # Her pattern için adresleri bul ve maskele
    for pattern in address_patterns:
        matches = re.findall(pattern, masked_text, re.IGNORECASE)
        for match in matches:
            # Her eşleşmeyi maskele
            masked_address = mask_address_in_text(match)
            masked_text = masked_text.replace(match, masked_address)
    
    return masked_text


def should_mask_data() -> bool:
    """
    Kişisel verilerin maskelenip maskelenmeyeceğini kontrol eder.
    Environment variable veya config'den okunabilir.
    
    Returns:
        True ise maskeleme aktif
    """
    import os
    # Default olarak aktif
    return os.getenv("MASK_PERSONAL_DATA", "true").lower() in ["true", "1", "yes"]


def mask_borclu_data(borclu_dict: dict, full_mask: bool = False) -> dict:
    """
    Borçlu bilgilerini içeren dictionary'deki kişisel verileri maskeler.
    
    Args:
        borclu_dict: Borçlu bilgileri dictionary
        full_mask: True ise tam maskeleme, False ise kısmi maskeleme
        
    Returns:
        Maskelenmiş borçlu bilgileri
    """
    masked = borclu_dict.copy()
    
    # TC/VKN maskeleme
    if 'tc_vkn' in masked and masked['tc_vkn']:
        mask_level = "full" if full_mask else "partial"
        masked['tc_vkn'] = mask_tc_vkn(masked['tc_vkn'], mask_level=mask_level)
    
    # Adres maskeleme
    if 'adres' in masked and masked['adres']:
        masked['adres'] = mask_address(masked['adres'], show_city=not full_mask)
    
    # Komiser isimleri - İsteğe bağlı maskeleme
    # Komiserler kamu görevlisi olduğu için genelde maskelenmeyebilir
    # Ama istenirse aktif edilebilir
    # if 'komiserler' in masked and masked['komiserler']:
    #     masked['komiserler'] = "****** [Gizli]"
    
    # Karar özeti ve metin içindeki kişisel verileri maskele
    if 'karar_ozeti' in masked and masked['karar_ozeti']:
        masked['karar_ozeti'] = mask_text_personal_data(masked['karar_ozeti'])
    
    return masked

