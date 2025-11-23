from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from models import Ilan, get_db_session

def temizle_metin(text):
    if not text: return ""
    return " ".join(text.split())

def normalize_tarih(tarih_str):
    """
    Tarih formatını standart hale getirir (GG.AA.YYYY)
    Desteklenen formatlar: 
    - 21/11/2025 -> 21.11.2025
    - 21.11.2025 -> 21.11.2025
    - 21-11-2025 -> 21.11.2025
    """
    if not tarih_str:
        return ""
    
    tarih_str = tarih_str.strip().replace(":", "").strip()
    
    # Boşlukları temizle
    tarih_str = " ".join(tarih_str.split())
    
    if not tarih_str:
        return ""
    
    # Farklı ayırıcıları normalize et
    # "/" veya "-" ile ayrılmış tarihleri "." ile değiştir
    import re
    # GG/AA/YYYY veya GG-AA-YYYY formatını GG.AA.YYYY'ye çevir
    tarih_str = re.sub(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', r'\1.\2.\3', tarih_str)
    
    # Eğer zaten "." ile ayrılmışsa ve format doğruysa olduğu gibi döndür
    if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', tarih_str):
        # Gün ve ayı 2 haneli yap (01.11.2025 gibi)
        parts = tarih_str.split('.')
        if len(parts) == 3:
            gun = parts[0].zfill(2)
            ay = parts[1].zfill(2)
            yil = parts[2]
            return f"{gun}.{ay}.{yil}"
        return tarih_str
    
    return tarih_str

def veri_cek_ve_kaydet():
    print("Veritabanına bağlanılıyor...")
    session = get_db_session()
    print("Veritabanı bağlantısı başarılı.")
    
    # Kullanıcıdan tarih aralığı iste
    print("\n--- Arama Filtreleri ---")
    print("Tarih formatı: GG.AA.YYYY (Örn: 18.11.2025)")
    baslangic_tarihi = input("Başlangıç Tarihi (Boş geçmek için Enter): ").strip()
    bitis_tarihi = input("Bitiş Tarihi (Boş geçmek için Enter): ").strip()
    
    base_path = "https://www.ilan.gov.tr/ilan/kategori/12/iflas-hukuku-davalari"
    
    if baslangic_tarihi or bitis_tarihi:
        # URL parametrelerini oluştur
        # txv=12 parametresi kategori seçimi için gerekli görünüyor
        params = ["txv=12"]
        if baslangic_tarihi:
            params.append(f"ppdmin={baslangic_tarihi}")
        if bitis_tarihi:
            params.append(f"ppdmax={bitis_tarihi}")
            
        target_url = f"{base_path}?{'&'.join(params)}"
    else:
        target_url = base_path
        
    base_url = "https://www.ilan.gov.tr"
    
    print(f"Hedef URL oluşturuldu: {target_url}")
    
    print("1. Selenium başlatılıyor...")
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-images")  # Resimleri yükleme (hızlandırma)
    chrome_options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2  # Görselleri devre dışı bırak
    })
    
    # Docker veya sunucu ortamı için headless modu
    if os.environ.get("HEADLESS", "false").lower() == "true":
        chrome_options.add_argument("--headless=new")
    else:
        chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(30)  # Sayfa yükleme zaman aşımı
    
    try:
        print(f"2. Siteye gidiliyor: {target_url}")
        driver.get(target_url)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results-row"))
            )
            # Sayfa tamamen yüklenene kadar bekle (Angular uygulaması için)
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            print(f"Zaman aşımı! İlan listesi yüklenemedi: {e}")
            return
        
        # Toplam sayfa sayısını bul
        toplam_sayfa = 1
        try:
            # Pagination container'ı bul
            pagination = driver.find_element(By.CSS_SELECTOR, "igt-pagination ul.ngx-pagination")
            # En son sayfa numarasını al (ellipsis'ten önceki son sayfa)
            sayfa_linkleri = pagination.find_elements(By.CSS_SELECTOR, "li a")
            for link in sayfa_linkleri:
                try:
                    sayfa_text = link.find_element(By.XPATH, ".//span[last()]").text.strip()
                    if sayfa_text.isdigit():
                        toplam_sayfa = max(toplam_sayfa, int(sayfa_text))
                except:
                    continue
            print(f"✓ Toplam {toplam_sayfa} sayfa tespit edildi.")
        except Exception as e:
            print(f"! Sayfa sayısı tespit edilemedi, sadece ilk sayfa taranacak. Hata: {e}")
        
        yeni_kayit_sayisi = 0
        main_window = driver.current_window_handle
        
        # Veritabanındaki mevcut ilan no'ları önbelleğe al (performans için)
        print("Mevcut ilanlar veritabanından yükleniyor...")
        mevcut_ilan_nolari = set(ilan.ilan_no for ilan in session.query(Ilan.ilan_no).all())
        print(f"✓ {len(mevcut_ilan_nolari)} mevcut ilan önbellekte.")
        
        # TÜM SAYFALARI TARA
        for sayfa_no in range(1, toplam_sayfa + 1):
            print(f"\n{'='*60}")
            print(f"SAYFA {sayfa_no}/{toplam_sayfa} İŞLENİYOR")
            print(f"{'='*60}")
            
            # Sayfa 1'den sonrası için URL'i güncelle
            if sayfa_no > 1:
                if '?' in target_url:
                    sayfa_url = f"{target_url}&currentPage={sayfa_no}"
                else:
                    sayfa_url = f"{target_url}?currentPage={sayfa_no}"
                
                print(f"Sayfa URL'si: {sayfa_url}")
                driver.get(sayfa_url)
                
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "search-results-row"))
                    )
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                except Exception as e:
                    print(f"! Sayfa {sayfa_no} yüklenemedi, atlanıyor: {e}")
                    continue
            
            # Sayfadaki ilanları bul - TEK SEFERDE
            ilan_kartlari = driver.find_elements(By.CSS_SELECTOR, "div.search-results-row")
            print(f"Bu sayfada {len(ilan_kartlari)} ilan bulundu.\n")
            
            # İlan verilerini topla (batch işlem için)
            ilan_verileri = []
            
            for i, row in enumerate(ilan_kartlari):
                try:
                    # Linki bul
                    parent_a = row.find_element(By.XPATH, "./ancestor::a")
                    link = parent_a.get_attribute("href")
                    
                    # Listeden hızlıca ilan no'yu yakala
                    row_text = row.text
                    gecici_ilan_no = ""
                    words = row_text.split()
                    for w in words:
                        if w.startswith("ILN") and len(w) < 15:
                            gecici_ilan_no = w
                            break
                    
                    # Önbellekten kontrol et (çok hızlı)
                    if gecici_ilan_no and gecici_ilan_no in mevcut_ilan_nolari:
                        print(f"[Sayfa {sayfa_no} - {i+1}/{len(ilan_kartlari)}] ATLANDI (Zaten var): {gecici_ilan_no}")
                        continue
                    
                    print(f"[Sayfa {sayfa_no} - {i+1}/{len(ilan_kartlari)}] İşleniyor... Link: {link}")
                    
                    # Detay sayfasına yeni sekmede git
                    driver.execute_script("window.open(arguments[0]);", link)
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # Detay sayfası yüklenene kadar bekle (daha akıllı)
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.single-ilan-header-inner h1"))
                        )
                    except:
                        pass
                    
                    detaylar = {
                        "ilan_no": gecici_ilan_no, "sehir": "", "ilce": "", 
                        "ilan_turu": "", "metin": "", "kurum": "", "baslik": "", "yayin_tarihi": ""
                    }
                    
                    # 1. Başlığı Al (Öncelikli)
                    try:
                        baslik_elem = driver.find_element(By.CSS_SELECTOR, "div.single-ilan-header-inner h1")
                        detaylar["baslik"] = baslik_elem.text.strip()
                    except:
                        pass

                    # 2. Sağ Panel Bilgileri
                    try:
                        bilgi_listesi = driver.find_elements(By.CSS_SELECTOR, "div.single-ilan-list ul li")
                        for li in bilgi_listesi:
                            try:
                                baslik_etiket = li.find_element(By.CLASS_NAME, "list-title").text.strip()
                                deger = li.find_element(By.CLASS_NAME, "list-desc").text.strip()
                                
                                if "İlan Numarası" in baslik_etiket: detaylar["ilan_no"] = deger
                                elif "Şehir" in baslik_etiket: detaylar["sehir"] = deger
                                elif "İlçe" in baslik_etiket: detaylar["ilce"] = deger
                                elif "İlan Türü" in baslik_etiket: detaylar["ilan_turu"] = deger
                                elif "İlan Sahibi" in baslik_etiket: detaylar["kurum"] = deger
                            except: continue
                        
                        # Yayın tarihini bul (Her iki formatta da <b> içinde)
                        for li in bilgi_listesi:
                            try:
                                li_text = li.text.lower()
                                # Yayın ile ilgili kelimeler varsa
                                if "yayın" in li_text or "yayım" in li_text:
                                    tarih_bold = li.find_element(By.TAG_NAME, "b")
                                    tarih = tarih_bold.text.strip()
                                    detaylar["yayin_tarihi"] = normalize_tarih(tarih)
                                    break
                            except:
                                continue
                    except: pass
                    
                    # 3. Metin
                    try:
                        content_div = driver.find_element(By.ID, "description-content")
                        detaylar["metin"] = temizle_metin(content_div.text)
                    except:
                        detaylar["metin"] = "Metin alınamadı"

                    # Veriyi listeye ekle (batch işlem için)
                    if detaylar["ilan_no"]:
                        if detaylar["ilan_no"] not in mevcut_ilan_nolari:
                            ilan_verileri.append({
                                "ilan_no": detaylar["ilan_no"],
                                "baslik": detaylar.get("baslik", ""),
                                "sehir": detaylar["sehir"],
                                "ilce": detaylar["ilce"],
                                "kurum": detaylar["kurum"],
                                "ilan_turu": detaylar["ilan_turu"],
                                "metin": detaylar["metin"],
                                "link": link,
                                "yayin_tarihi": detaylar["yayin_tarihi"]
                            })
                            mevcut_ilan_nolari.add(detaylar["ilan_no"])  # Önbelleğe ekle
                            print(f"   ✓ Veriler toplandı: {detaylar['ilan_no']}")
                        else:
                            print(f"   . Zaten mevcut.")
                    else:
                        print("   ! İlan No bulunamadı, kaydedilmedi.")

                    # Sekmeyi kapat
                    driver.close()
                    driver.switch_to.window(main_window)
                    
                except Exception as e:
                    print(f"Satır hatası: {e}")
                    # Hata durumunda sekmeleri temizle
                    while len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                    driver.switch_to.window(main_window)
            
            # Her sayfa sonunda batch olarak veritabanına yaz
            if ilan_verileri:
                print(f"\n{'~'*60}")
                print(f"Sayfa {sayfa_no} için {len(ilan_verileri)} ilan veritabanına yazılıyor...")
                try:
                    for veri in ilan_verileri:
                        yeni_ilan = Ilan(**veri)
                        session.add(yeni_ilan)
                    session.commit()
                    yeni_kayit_sayisi += len(ilan_verileri)
                    print(f"✓ {len(ilan_verileri)} ilan başarıyla kaydedildi!")
                except Exception as e:
                    # Eğer duplicate key hatası varsa (nadiren olabilir)
                    if 'Duplicate entry' in str(e) or 'unique constraint' in str(e).lower():
                        print(f"⚠ Duplicate ilan tespit edildi, tekil kayıt moduna geçiliyor...")
                        session.rollback()
                        basarili = 0
                        # Tek tek kayıt dene
                        for veri in ilan_verileri:
                            try:
                                # DB'den tekrar kontrol et
                                mevcut = session.query(Ilan).filter_by(ilan_no=veri["ilan_no"]).first()
                                if not mevcut:
                                    yeni_ilan = Ilan(**veri)
                                    session.add(yeni_ilan)
                                    session.commit()
                                    basarili += 1
                                else:
                                    print(f"   • {veri['ilan_no']} atlandı (duplicate)")
                            except Exception as ex:
                                print(f"   ✗ {veri.get('ilan_no', '?')} hatası: {ex}")
                                session.rollback()
                        yeni_kayit_sayisi += basarili
                        print(f"✓ {basarili}/{len(ilan_verileri)} ilan kaydedildi (tekil mod)")
                    else:
                        print(f"✗ Veritabanı hatası: {e}")
                        session.rollback()
                print(f"{'~'*60}\n")

        print(f"\n{'='*60}")
        print(f"TARAMA TAMAMLANDI!")
        print(f"Toplam {toplam_sayfa} sayfa tarandı.")
        print(f"{yeni_kayit_sayisi} yeni ilan veritabanına eklendi.")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        driver.quit()
        session.close()

if __name__ == "__main__":
    veri_cek_ve_kaydet()

