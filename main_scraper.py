from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from models import Ilan, get_db_session

def temizle_metin(text):
    if not text: return ""
    return " ".join(text.split())

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
    chrome_options.add_argument("--start-maximized")
    
    # Docker veya sunucu ortamı için headless modu
    import os
    if os.environ.get("HEADLESS", "false").lower() == "true":
        chrome_options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print(f"2. Siteye gidiliyor: {target_url}")
        driver.get(target_url)
        
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "search-results-row")))
        except:
            print("Zaman aşımı! İlan listesi yüklenemedi.")
            return

        time.sleep(3)
        ilan_kartlari = driver.find_elements(By.CSS_SELECTOR, "div.search-results-row")
        print(f"\n--- {len(ilan_kartlari)} İLAN BULUNDU ---\n")
        
        yeni_kayit_sayisi = 0
        
        # Selenium elementleri bayatlayabilir (stale element), bu yüzden index ile gezelim veya listeyi yenileyelim
        # Ancak basit bir döngüde yeni sekmeye gidip gelmek ana sayfayı bozmazsa sorun olmaz.
        # Güvenli yöntem: Her seferinde ana pencere handle'ını sakla.
        
        main_window = driver.current_window_handle
        
        for i in range(len(ilan_kartlari)):
            try:
                # Elementler bayatlamış olabilir, listeyi tekrar bul
                kartlar_tekrar = driver.find_elements(By.CSS_SELECTOR, "div.search-results-row")
                if i >= len(kartlar_tekrar): break
                
                row = kartlar_tekrar[i]
                
                # Linki bul
                parent_a = row.find_element(By.XPATH, "./ancestor::a")
                link = parent_a.get_attribute("href")
                
                # Ön kontrol: Link veritabanında var mı? (İlan no'yu henüz bilmiyoruz ama link unique olabilir)
                # İlan no daha kesin olduğu için detaya girip bakmak en garantisi ama yavaşlatır.
                # Listeden hızlıca bir "ILN..." yakalamaya çalışalım
                row_text = row.text
                gecici_ilan_no = ""
                words = row_text.split()
                for w in words:
                    if w.startswith("ILN") and len(w) < 15:
                        gecici_ilan_no = w
                        break
                
                if gecici_ilan_no:
                    mevcut = session.query(Ilan).filter_by(ilan_no=gecici_ilan_no).first()
                    if mevcut:
                        print(f"[{i+1}/{len(ilan_kartlari)}] ATLANDI (Zaten var): {gecici_ilan_no}")
                        continue
                
                print(f"[{i+1}/{len(ilan_kartlari)}] İşleniyor... Link: {link}")
                
                # Detay sayfasına yeni sekmede git
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[-1])
                
                time.sleep(2) # Yükleme beklemesi
                
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
                                tarih = tarih_bold.text.strip().replace(":", "").strip()
                                detaylar["yayin_tarihi"] = tarih
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

                # VERİTABANINA YAZ
                if detaylar["ilan_no"]:
                    mevcut = session.query(Ilan).filter_by(ilan_no=detaylar["ilan_no"]).first()
                    if not mevcut:
                        yeni_ilan = Ilan(
                            ilan_no=detaylar["ilan_no"],
                            baslik=detaylar.get("baslik", ""),
                            sehir=detaylar["sehir"],
                            ilce=detaylar["ilce"],
                            kurum=detaylar["kurum"],
                            ilan_turu=detaylar["ilan_turu"],
                            metin=detaylar["metin"],
                            link=link,
                            yayin_tarihi=detaylar["yayin_tarihi"]
                        )
                        session.add(yeni_ilan)
                        session.commit()
                        yeni_kayit_sayisi += 1
                        print(f"   + KAYIT BAŞARILI: {detaylar['ilan_no']}")
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

        print(f"\nTarama Tamamlandı. {yeni_kayit_sayisi} yeni ilan eklendi.")

    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        driver.quit()
        session.close()

if __name__ == "__main__":
    veri_cek_ve_kaydet()

