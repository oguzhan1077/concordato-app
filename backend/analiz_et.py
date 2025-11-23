import json
from openai import OpenAI
from models import Ilan, IlanBorclu, get_db_session
from config import OPENAI_API_KEY
import time

# OpenAI İstemcisi
if not OPENAI_API_KEY:
    print("UYARI: Lütfen config.py dosyasina gecerli bir OpenAI API Key girin!")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY)

# Maliyet Katsayıları (gpt-4o-mini)
COST_INPUT_1M = 0.15
COST_OUTPUT_1M = 0.60

def hesapla_maliyet(usage):
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    cost = (input_tokens / 1_000_000 * COST_INPUT_1M) + (output_tokens / 1_000_000 * COST_OUTPUT_1M)
    return cost

# Karar Türleri Listesi
KARAR_TURLERI = [
    "Alacak Bildirme Daveti", "Alacaklar Kurulu", "Alacaklılar Kurulunun Oluşturulması Kararı",
    "Alacaklılar Toplantısı İlanı", "Alacaklılar Toplantısının Ertelenmesi Duyurusu", "Ara Karar",
    "Çekişmeli Alacak İlanı", "Duruşmanın Ertelenmesi Duyurusu", "Duyuru", "Düzeltme Kararı",
    "Ek Karar", "Geçici Mühlet Kararı", "Geçici Mühlet Uzatma Kararı", "İflas – Konkordato Toplantı Daveti",
    "İflas Başvurusuna İtiraz Hakkı Tebliği", "İflas Kararı", "İflasın Kaldırılması Kararı",
    "Kayyum Atanması Kararı", "Kayyumun Görevine Son Verildi", "Kesin Mühlet Kararı",
    "Kesin Mühlet Uzatma Kararı", "Komiser Atanması Duyurusu", "Komiser Değişikliği Duyurusu",
    "Komiser Heyeti Raporu", "Komiser Heyetinin Yetkilendirilmesi", "Konkordato Başarı ile Sonuçlanmıştır",
    "Konkordato Başvurusu", "Konkordato Tasdik Kararı", "Konkordatonun Reddi Kararı",
    "Konkordatoya İtiraz Hakkı Tebliği", "Mal Varlığı Satış İlanı", "Tedbir ve Tedbir Şerhlerinin Kaldırılması Kararı",
    "Genel İflas Duyurusu", "Genel Konkordato Duyurusu", "Genel Tasfiye Duyurusu", "Diğer"
]

def analiz_et_ve_kaydet():
    session = get_db_session()
    print("Veritabanına bağlanıldı.")

    # 1. Analiz edilmemiş ilanları bul
    # Yöntem: IlanBorclu tablosunda ID'si olmayan ilanları seç
    # İpucu: Eğer analizi başarısız olanları tekrar denemek istemiyorsanız buraya bir 'status' kolonu eklemek gerekebilir.
    # Şimdilik basit mantık: Borçlu kaydı yoksa analiz et.
    
    # --- TEKİL İLAN GÜNCELLEME MODU ---
    # Belirli bir ilanı (veya ilanları) tekrar analiz etmek için burayı kullanıyoruz.
    # Bu modda, ilanın daha önce analiz edilip edilmediğine bakılmaksızın analiz yapılır.
    hedef_ilan_no = "ILN02338838"  # Güncellenecek ilan no
    analiz_bekleyenler = session.query(Ilan).filter(Ilan.ilan_no == hedef_ilan_no).all()
    
    # Eğer tekil mod kapalıysa (hedef_ilan_no boşsa veya yorum satırıysa) aşağıdaki blok çalışır:
    if not analiz_bekleyenler:
        subquery = session.query(IlanBorclu.ilan_id).distinct()
        # Limiti kaldırıyoruz, tüm bekleyenleri işle
        analiz_bekleyenler = session.query(Ilan).filter(Ilan.id.notin_(subquery)).all() 
    # ----------------------------------
    
    if not analiz_bekleyenler:
        print("Analiz edilecek yeni ilan bulunamadı.")
        return

    print(f"Analiz edilecek {len(analiz_bekleyenler)} ilan bulundu.")
    
    for ilan in analiz_bekleyenler:
        print(f"Analiz ediliyor: {ilan.ilan_no}")
        
        # Eski analiz sonuçlarını temizle (Sadece tekil güncelleme yapıyorsak mantıklı)
        if hedef_ilan_no and ilan.ilan_no == hedef_ilan_no:
            print(f"   ! {ilan.ilan_no} için eski kayıtlar siliniyor...")
            session.query(IlanBorclu).filter(IlanBorclu.ilan_id == ilan.id).delete()
            session.commit()

        try:
            prompt = f"""
            Sen deneyimli bir hukuk asistanısın. Aşağıdaki resmi ilan metnini analiz et ve içindeki borçlu kişi veya kurumları tespit et.
            Bir ilanda birden fazla borçlu (şirket ve ortakları gibi) olabilir. Hepsi için ayrı nesne oluştur.
            
             İLAN METNİ:
             {ilan.metin}
             
             KARAR TÜRLERİ LİSTESİ:
             {", ".join(KARAR_TURLERI)}
             
            GÖREV:
            Aşağıdaki JSON şemasına tam olarak uyarak veriyi çıkar. Eğer bir bilgi metinde yoksa null (None) olarak bırak.
            
            ÖNEMLİ KURALLAR:
            1. "karar_turu" alanını YUKARIDAKİ LİSTEDEN seç.
               - "Konkordato Başvurusu": SADECE davanın yeni açıldığı veya geçici mühlet talebinin ilan edildiği durumlarda seç.
               - Eğer metinde "Ara Karar Gereğince" ifadesi varsa ve içerik komiser değişikliği, bilirkişi raporu vb. ise "Ara Karar" veya "Komiser Değişikliği Duyurusu" seç.
               - Eğer komiser atanması veya değişmesi söz konusuysa, EN UYGUN seçenek "Komiser Değişikliği Duyurusu" veya "Komiser Atanması Duyurusu"dur. "Konkordato Başvurusu" seçme.
            2. "muhlet_suresi" alanına dikkat et: Metinde eski kararlardan bahsedilebilir. Sen her zaman **en son verilen kararın** süresini yaz. Örneğin "önce 3 ay verildi, şimdi 2 ay uzatıldı" diyorsa, mühlet süresi "2 Ay Uzatma" veya "2 Ay" olmalıdır.
            3. KARAR ÖNCELİĞİ VE HİYERARŞİSİ (ÇOK ÖNEMLİ):
               - Bir borçlu için birden fazla hüküm varsa, EN AĞIR/NİHAİ sonucu seç.
               - ÖNCELİK SIRASI: **İFLAS KARARI** > **KONKORDATONUN REDDİ KARARI** > **KESİN MÜHLET** > **GEÇİCİ MÜHLET**.
               - ÖRNEK: Metinde "Konkordato talebinin reddi ile İFLASINA" yazıyorsa, karar türü mutlaka "İflas Kararı" olmalıdır. Sadece "Konkordatonun Reddi Kararı" seçme.
            4. BAĞIMSIZ DEĞERLENDİRME: 
               - İlan içinde birden fazla firma/kişi olabilir ve her biri için FARKLI kararlar verilmiş olabilir.
               - Hepsine aynı kararı atama! Metni dikkatlice oku ve hangi hükmün hangi firmaya ait olduğunu ayırt et.
               - ÖRNEK: A Firması için "İflasına", B Firması için "Konkordato Reddine" denmişse; A'nın kararı "İflas Kararı", B'nin kararı "Konkordatonun Reddi Kararı" olmalıdır.
            5. GRUPLANMIŞ HÜKÜMLER VE AYRIŞTIRMA (ÇOK ÖNEMLİ):
               - Metinde firmalar gruplara ayrılmış olabilir. Her grubun kendi hükmünü (kararını) uygula.
               - "A, B ve C'nin ... İFLASINA, D'nin ... REDDİNE" şeklinde bir yapı varsa:
                 * A, B, C -> İflas Kararı
                 * D -> Konkordatonun Reddi Kararı (Çünkü D için ayrıca iflas denmemiş)
               - "İFLASINA" kelimesi, kendisinden ÖNCE sıralanan firmaları bağlar. Kendisinden SONRA gelen yeni cümlenin öznesi olan firmayı bağlamaz.
               - Noktalama işaretlerine (virgül, nokta) ve bağlaçlara ("ile", "ve") dikkat et. Hüküm nerede bitiyor, yeni hüküm nerede başlıyor analiz et.
            6. Davanın tarafları (şahıslar) için metinde özel bir hüküm yoksa bile, davanın genel sonucunu onlara da uygula. Ancak metinde bir SONUÇ yoksa uydurma.
            7. "karar_ozeti" alanına, metinde geçen kararın KISA ve NET bir özetini yaz. ASLA buradaki örnek metni kopyalama. Metni kendin özetle.
            8. TARİHLERİ AYIRT ET:
               - "karar_tarihi": Mahkemenin kararı verdiği/imzaladığı tarih.
               - "karar_baslangic_tarihi": Sürenin işlemeye başladığı tarih (Genelde "...tarihinden itibaren" veya "...saatinden başlamak üzere" yazar). Eğer belirtilmemişse karar tarihini al.
               - "durusma_tarihi": Gelecekteki duruşma tarihi.
            9. HALÜSİNASYON ENGELLEME VE DOĞRULUK (KRİTİK):
               - "muhlet_suresi" alanına, SADECE ve SADECE metinde AÇIKÇA belirtilen süreleri yaz (Örn: "3 ay süreyle", "2 ay uzatılmasına").
               - Eğer metinde süre geçmiyorsa, ASLA tahmin etme, "2 ay uzatıldı" gibi uydurma bilgiler yazma. Bu alanı null bırak.
               - Metinde "yerine ... görevlendirilmesine", "görevine son verilmesine" veya "istifasının kabulüne" gibi ifadeler varsa, Karar Türü olarak mutlaka "Komiser Değişikliği Duyurusu" seç.
               - Metinde "Geçici mühlet ara raporları..." ifadesi tek başına bir mühlet kararı değildir. Sonuç kısmına bak.

            İSTENEN JSON ÇIKTISI (Liste Formatında):
            {{
                "borclular": [
                    {{
                        "borclu_adi": "Şirket veya Kişi Tam Adı",
                        "borclu_tipi": "TUZEL_KISI" veya "GERCEK_KISI",
                        "tc_vkn": "Sadece rakamlardan oluşan VKN veya TC No",
                        "ticaret_sicil_no": "Sicil numarası",
                        "adres": "Adres metni",
                        "karar_turu": "Listeden seçilen karar türü",
                        "karar_ozeti": "Kararın özeti",
                        "karar_tarihi": "GG.MM.YYYY",
                        "karar_baslangic_tarihi": "GG.MM.YYYY",
                        "muhlet_suresi": "Örn: 3 Ay",
                        "mahkeme_adi": "Kararı veren mahkeme",
                        "dosya_esas_no": "Örn: 2024/123",
                        "komiserler": "Komiser isimleri (Ali Veli, Ayşe Fatma...)",
                        "durusma_tarihi": "GG.MM.YYYY"
                    }}
                ]
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Hızlı ve ucuz model
                messages=[
                    {"role": "system", "content": "Sen JSON çıktısı veren bir hukuk analiz motorusun."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.1 # Yaratıcılık değil, kesinlik istiyoruz
            )
            
            # Maliyet Hesabı
            cost = hesapla_maliyet(response.usage)
            print(f"   > Maliyet: ${cost:.6f}")
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            borclular_listesi = data.get("borclular", [])
            
            if not borclular_listesi:
                print("   ! Metinde borçlu bulunamadı veya yapı çözülemedi.")
            
            for item in borclular_listesi:
                yeni_borclu = IlanBorclu(
                    ilan_id=ilan.id,
                    borclu_adi=item.get("borclu_adi"),
                    borclu_tipi=item.get("borclu_tipi"),
                    tc_vkn=item.get("tc_vkn"),
                    ticaret_sicil_no=item.get("ticaret_sicil_no"),
                    adres=item.get("adres"),
                    karar_turu=item.get("karar_turu"),
                    karar_ozeti=item.get("karar_ozeti"),
                    karar_tarihi=item.get("karar_tarihi"),
                    karar_baslangic_tarihi=item.get("karar_baslangic_tarihi"),
                    muhlet_suresi=item.get("muhlet_suresi"),
                    mahkeme_adi=item.get("mahkeme_adi"),
                    dosya_esas_no=item.get("dosya_esas_no"),
                    komiserler=item.get("komiserler"),
                    durusma_tarihi=item.get("durusma_tarihi")
                )
                session.add(yeni_borclu)
                print(f"   + Eklendi: {item.get('borclu_adi')}")
            
            session.commit()
            
        except Exception as e:
            print(f"   ! Hata: {e}")
            session.rollback()
        
        # Rate limit dostu bekleme
        time.sleep(0.5)

    session.close()
    print("İşlem tamamlandı.")

if __name__ == "__main__":
    analiz_et_ve_kaydet()

