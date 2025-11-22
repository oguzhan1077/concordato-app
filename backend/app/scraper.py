from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from .models import Ilan
from .database import SessionLocal

def temizle_metin(text):
    if not text: return ""
    return " ".join(text.split())

def veri_cek_ve_kaydet(baslangic_tarihi=None, bitis_tarihi=None):
    print("Veritabanına bağlanılıyor...")
    session = SessionLocal()
    print("Veritabanı bağlantısı başarılı.")
    
    # Environment variable kontrolü
    if not baslangic_tarihi:
        baslangic_tarihi = os.getenv("BASLANGIC_TARIHI", "").strip()
    if not bitis_tarihi:
        bitis_tarihi = os.getenv("BITIS_TARIHI", "").strip()
    
    base_path = "https://www.ilan.gov.tr/ilan/kategori/12/iflas-hukuku-davalari"
    
    if baslangic_tarihi or bitis_tarihi:
        params = ["txv=12"]
        if baslangic_tarihi:
            params.append(f"ppdmin={baslangic_tarihi}")
        if bitis_tarihi:
            params.append(f"ppdmax={bitis_tarihi}")
            
        target_url = f"{base_path}?{'&'.join(params)}"
    else:
        target_url = base_path
        
    print(f"Hedef URL oluşturuldu: {target_url}")
    
    print("1. Selenium başlatılıyor...")
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2
    })
    
    # Her zaman headless
    chrome_options.add_argument("--headless=new")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(30)
    except Exception as e:
        print(f"Chrome driver başlatılamadı: {e}")
        session.close()
        return
    
    try:
        print(f"2. Siteye gidiliyor: {target_url}")
        driver.get(target_url)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results-row"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            print(f"Zaman aşımı! İlan listesi yüklenemedi: {e}")
            return
        
        toplam_sayfa = 1
        try:
            pagination = driver.find_element(By.CSS_SELECTOR, "igt-pagination ul.ngx-pagination")
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
        
        print("Mevcut ilanlar veritabanından yükleniyor...")
        mevcut_ilan_nolari = set(ilan.ilan_no for ilan in session.query(Ilan.ilan_no).all())
        print(f"✓ {len(mevcut_ilan_nolari)} mevcut ilan önbellekte.")
        
        for sayfa_no in range(1, toplam_sayfa + 1):
            print(f"\n{'='*60}")
            print(f"SAYFA {sayfa_no}/{toplam_sayfa} İŞLENİYOR")
            print(f"{'='*60}")
            
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
            
            ilan_kartlari = driver.find_elements(By.CSS_SELECTOR, "div.search-results-row")
            print(f"Bu sayfada {len(ilan_kartlari)} ilan bulundu.\n")
            
            ilan_verileri = []
            
            for i, row in enumerate(ilan_kartlari):
                try:
                    parent_a = row.find_element(By.XPATH, "./ancestor::a")
                    link = parent_a.get_attribute("href")
                    
                    row_text = row.text
                    gecici_ilan_no = ""
                    words = row_text.split()
                    for w in words:
                        if w.startswith("ILN") and len(w) < 15:
                            gecici_ilan_no = w
                            break
                    
                    if gecici_ilan_no and gecici_ilan_no in mevcut_ilan_nolari:
                        print(f"[Sayfa {sayfa_no} - {i+1}/{len(ilan_kartlari)}] ATLANDI (Zaten var): {gecici_ilan_no}")
                        continue
                    
                    print(f"[Sayfa {sayfa_no} - {i+1}/{len(ilan_kartlari)}] İşleniyor... Link: {link}")
                    
                    driver.execute_script("window.open(arguments[0]);", link)
                    driver.switch_to.window(driver.window_handles[-1])
                    
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
                    
                    try:
                        baslik_elem = driver.find_element(By.CSS_SELECTOR, "div.single-ilan-header-inner h1")
                        detaylar["baslik"] = baslik_elem.text.strip()
                    except: pass

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
                        
                        for li in bilgi_listesi:
                            try:
                                li_text = li.text.lower()
                                if "yayın" in li_text or "yayım" in li_text:
                                    tarih_bold = li.find_element(By.TAG_NAME, "b")
                                    tarih = tarih_bold.text.strip().replace(":", "").strip()
                                    detaylar["yayin_tarihi"] = tarih
                                    break
                            except: continue
                    except: pass
                    
                    try:
                        content_div = driver.find_element(By.ID, "description-content")
                        detaylar["metin"] = temizle_metin(content_div.text)
                    except:
                        detaylar["metin"] = "Metin alınamadı"

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
                            mevcut_ilan_nolari.add(detaylar["ilan_no"])
                            print(f"   ✓ Veriler toplandı: {detaylar['ilan_no']}")
                        else:
                            print(f"   . Zaten mevcut.")
                    else:
                        print("   ! İlan No bulunamadı, kaydedilmedi.")

                    driver.close()
                    driver.switch_to.window(main_window)
                    
                except Exception as e:
                    print(f"Satır hatası: {e}")
                    while len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                    driver.switch_to.window(main_window)
            
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
                    if 'Duplicate entry' in str(e) or 'unique constraint' in str(e).lower():
                        print(f"⚠ Duplicate ilan tespit edildi, tekil kayıt moduna geçiliyor...")
                        session.rollback()
                        basarili = 0
                        for veri in ilan_verileri:
                            try:
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
        try:
            driver.quit()
        except:
            pass
        session.close()

if __name__ == "__main__":
    veri_cek_ve_kaydet()

