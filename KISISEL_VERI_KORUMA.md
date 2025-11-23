# Kişisel Veri Koruma Sistemi

## Genel Bakış

Bu sistem, **KVKK (Kişisel Verilerin Korunması Kanunu)** ve **TCK Madde 136** uyarınca kişisel verilerin korunması için geliştirilmiştir.

### Yasal Gerekçe

Türk Ceza Kanunu Madde 136'ya göre, **kişisel verilerin kaydedilmesi, ifşa edilmesi ve yok edilmemesi suçtur**. Kişisel veriler şunları içerir:

- T.C. Kimlik Numarası
- Vergi Kimlik Numarası (VKN)
- Telefon Numaraları
- E-posta Adresleri
- Tam Adres Bilgileri

Bu nedenle, sistemimiz bu verileri **otomatik olarak maskeler** ve güvenli bir şekilde saklar.

---

## Maskeleme Sistemi

### 1. Backend (API) Maskeleme

API response'larında kişisel veriler otomatik olarak maskelenir.

#### Maskeleme Türleri

| Veri Türü | Orijinal | Maskelenmiş | Açıklama |
|-----------|----------|-------------|----------|
| TC Kimlik No | 12345678901 | 123****8901 | İlk 3 ve son 4 hane görünür |
| VKN | 1234567890 | 123****890 | İlk 3 ve son 3 hane görünür |
| Telefon | 0532 123 45 67 | 0532 *** ** ** | Alan kodu görünür |
| E-posta | test@example.com | t***@example.com | İlk harf görünür |
| Adres | Atatürk Mah. ... İstanbul | ****** İstanbul | Sadece şehir görünür |

#### Maskeleme Seviyesi

**Kısmi Maskeleme (Partial)**: Varsayılan mod. Doğrulama için minimum bilgi görünür.
**Tam Maskeleme (Full)**: Tüm veriler tamamen gizlenir (`***********`).

### 2. Metin İçi Maskeleme

İlan metinlerindeki kişisel veriler otomatik olarak tespit edilir ve maskelenir:

- 11 haneli sayılar (TC/VKN olabilir)
- Telefon numarası formatları
- E-posta adresleri
- "TC:", "VKN:", "Vergi No:" etiketli veriler

### 3. Frontend Gösterimi

Frontend'de maskelenmiş veriler **kilit simgesi (🔒)** ile işaretlenir.

---

## Kullanım

### Maskelemeyi Aktif/Pasif Etme

Maskeleme varsayılan olarak **aktif**tir. Devre dışı bırakmak için:

**Environment Variable ile:**
```bash
export MASK_PERSONAL_DATA=false
```

**Docker Compose ile:**
```yaml
environment:
  - MASK_PERSONAL_DATA=false
```

**Config dosyasında:**
```python
# backend/config.py
MASK_PERSONAL_DATA = "false"
```

⚠️ **UYARI**: Maskelemeyi devre dışı bırakmak yasal sorumluluğu artırır!

---

## Teknik Detaylar

### Backend Modülleri

#### `privacy_utils.py`
Maskeleme fonksiyonlarını içerir:

- `mask_tc_vkn()` - TC/VKN maskeleme
- `mask_phone()` - Telefon maskeleme
- `mask_email()` - E-posta maskeleme
- `mask_address()` - Adres maskeleme
- `mask_text_personal_data()` - Metin içi otomatik maskeleme
- `mask_borclu_data()` - Borçlu dictionary'si maskeleme

#### `schemas.py`
Pydantic model'lerinde otomatik maskeleme:

- `IlanBorclu.mask_personal_data()` - Borçlu bilgilerini maskeler
- `Ilan.mask_personal_data_in_text()` - İlan metnini maskeler

### Maskeleme İş Akışı

```
1. Scraper → Ham veri toplar
2. Analiz (OpenAI) → Kişisel verileri çıkarır
3. Veritabanı → Ham veri saklanır (şifreli)
4. API Response → Otomatik maskeleme uygulanır (Pydantic validator)
5. Frontend → Maskelenmiş veri görüntülenir
```

---

## Örnekler

### Python'da Kullanım

```python
from backend.app.privacy_utils import mask_tc_vkn, mask_address, mask_phone

# TC maskeleme
tc = "12345678901"
masked_tc = mask_tc_vkn(tc, mask_level="partial")
print(masked_tc)  # 123****8901

# Adres maskeleme
adres = "Atatürk Mah. Cumhuriyet Cad. No:123 Kadıköy/İstanbul"
masked_adres = mask_address(adres, show_city=True)
print(masked_adres)  # ****** İstanbul

# Telefon maskeleme
telefon = "0532 123 45 67"
masked_telefon = mask_phone(telefon)
print(masked_telefon)  # 0532 *** ** **
```

### API Response Örneği

```json
{
  "id": 1,
  "borclu_adi": "ABC Şirketi",
  "tc_vkn": "123****8901",
  "adres": "****** İstanbul",
  "karar_ozeti": "Şirketin konkordato talebi kabul edilmiştir. TC No: *********** olan..."
}
```

---

## Güvenlik En İyi Uygulamaları

### ✅ Yapılması Gerekenler

1. **Maskelemeyi aktif tutun** - Yasal gereklilik
2. **Loglarda kişisel veri bulundurmayın**
3. **Veritabanı yedeklerini şifreleyin**
4. **HTTPS kullanın** - İletimde şifreleme
5. **Erişim kontrolü uygulayın** - Kimlik doğrulama

### ❌ Yapılmaması Gerekenler

1. **Ham TC/VKN'yi API'de döndürmeyin**
2. **Kişisel verileri URL'de göndermeyin**
3. **Public log dosyalarında kişisel veri bulundurmayın**
4. **Maskeleme olmadan frontend'e veri göndermeyin**

---

## Yasal Uyumluluk

### KVKK Madde 12
> "Kişisel verilerin güvenliğini sağlamak için teknik ve idari tedbirler alınmalıdır."

### TCK Madde 136
> "Kişisel verileri hukuka aykırı olarak kaydeden, veren veya yayan kişi, 2 yıldan 4 yıla kadar hapis cezası ile cezalandırılır."

### Uyumluluk Kontrol Listesi

- [x] Kişisel veriler maskeleniyor
- [x] API response'larında otomatik koruma
- [x] Frontend'de görsel göstergeler
- [x] Environment variable ile kontrol
- [x] Dokümantasyon mevcut
- [ ] Veritabanı şifreleme (isteğe bağlı)
- [ ] Veri silme politikası (KVKK Madde 7)
- [ ] Kullanıcı onayı mekanizması

---

## Sık Sorulan Sorular

### S: Maskeleme performansı etkiler mi?
**C:** Hayır, maskeleme sadece API response aşamasında yapılır ve çok hızlıdır.

### S: Veritabanında ham veri mi saklanıyor?
**C:** Evet, analiz ve işleme için ham veri saklanır, ancak API'de asla döndürülmez.

### S: Maskelemeyi kullanıcı bazında değiştirebilir miyiz?
**C:** Evet, `mask_borclu_data()` fonksiyonunu kullanıcı rol bazında çağırabilirsiniz.

### S: Komiser isimleri neden maskelenmiyor?
**C:** Komiserler kamu görevlisi olduğu için genelde kamu bilgisi sayılır. İstenirse maskeleme aktif edilebilir.

---

## Destek ve İletişim

Kişisel veri koruma ile ilgili sorularınız için:

1. Dokümantasyonu inceleyin
2. `privacy_utils.py` kodunu gözden geçirin
3. KVKK uzmanınıza danışın

---

**Son Güncelleme:** 23 Kasım 2025  
**Versiyon:** 1.0.0  
**Yasal Uyumluluk:** KVKK & TCK 136

