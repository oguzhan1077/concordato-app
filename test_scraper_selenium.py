from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def temizle_metin(text):
    """Metindeki fazla boşlukları ve gereksiz karakterleri temizler"""
    if not text: return ""
    return " ".join(text.split())

def test_et():
    base_url = "https://www.ilan.gov.tr"
    target_url = "https://www.ilan.gov.tr/ilan/kategori/12/iflas-hukuku-davalari"
    
    print("1. Selenium ile tarayıcı başlatılıyor...")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print(f"2. Siteye gidiliyor: {target_url}")
        driver.get(target_url)
        
        print("3. Verilerin yüklenmesi bekleniyor...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results-row"))
            )
        except:
            print("Zaman aşımı: İlanlar yüklenemedi.")
            return
        
        time.sleep(3)
        
        ilan_kartlari = driver.find_elements(By.CSS_SELECTOR, "div.search-results-row")
        print(f"\n--- {len(ilan_kartlari)} ADET İLAN BULUNDU ---\n")
        
        count = 0
        for row in ilan_kartlari:
            if count >= 1: break # Test için sadece 1 ilan yeterli
            
            try:
                # Linki bul
                parent_a = row.find_element(By.XPATH, "./ancestor::a")
                link = parent_a.get_attribute("href")
                
                print(f"Link Bulundu: {link}")
                
                # --- DETAY SAYFASINA GİTME ---
                print("   > Detay çekiliyor...")
                
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[-1])
                
                time.sleep(3)
                
                detaylar = {
                    "ilan_no": "", "sehir": "", "ilce": "", 
                    "dosya_no": "", "ilan_turu": "", "metin": ""
                }
                
                try:
                    # 1. İLAN BİLGİLERİ (Sağ Panel)
                    # single-ilan-list içindeki li'leri gez
                    bilgi_listesi = driver.find_elements(By.CSS_SELECTOR, "div.single-ilan-list ul li")
                    
                    for li in bilgi_listesi:
                        try:
                            baslik = li.find_element(By.CLASS_NAME, "list-title").text.strip()
                            deger = li.find_element(By.CLASS_NAME, "list-desc").text.strip()
                            
                            if "İlan Numarası" in baslik: detaylar["ilan_no"] = deger
                            elif "Şehir" in baslik: detaylar["sehir"] = deger
                            elif "İlçe" in baslik: detaylar["ilce"] = deger
                            elif "Dosya Numarası" in baslik: detaylar["dosya_no"] = deger
                            elif "İlan Türü" in baslik: detaylar["ilan_turu"] = deger
                        except:
                            continue

                    # 2. İLAN METNİ (Sol Panel)
                    # id="description-content" olan div
                    try:
                        content_div = driver.find_element(By.ID, "description-content")
                        detaylar["metin"] = temizle_metin(content_div.text)
                    except:
                        detaylar["metin"] = "Metin bulunamadı"

                    # SONUÇLARI YAZDIR
                    print("\n   --- ÇEKİLEN DETAYLAR ---")
                    print(f"   İlan No   : {detaylar['ilan_no']}")
                    print(f"   Şehir     : {detaylar['sehir']}")
                    print(f"   İlçe      : {detaylar['ilce']}")
                    print(f"   Dosya No  : {detaylar['dosya_no']}")
                    print(f"   İlan Türü : {detaylar['ilan_turu']}")
                    print(f"   Metin     : {detaylar['metin'][:150]}...") # İlk 150 karakter
                    
                except Exception as e:
                    print(f"   ! Detay ayrıştırma hatası: {e}")
                
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print("-" * 60)
                count += 1
                
            except Exception as e:
                print(f"Hata: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_et()