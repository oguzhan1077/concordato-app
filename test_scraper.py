import requests
from bs4 import BeautifulSoup
import time
import random

import urllib3

# SSL Uyarilarini gizle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_et():
    # Hedef URL
    base_url = "https://www.ilan.gov.tr"
    target_url = "https://www.ilan.gov.tr/ilan/kategori/12/iflas-hukuku-davalari"
    
    # Tarayıcı taklidi yapan başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"1. Siteye bağlanılıyor: {target_url}")
    
    try:
        # verify=False ile SSL hatasini asiyoruz
        response = requests.get(target_url, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"HATA: Siteye erişilemedi. Durum Kodu: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # İlan kartlarını bul (Sizin verdiğiniz HTML yapısına göre)
        # <a href="..."> içinde <div class="search-results-row"> arıyoruz
        ilan_linkleri = soup.find_all("a", href=True)
        
        bulunan_ilan_sayisi = 0
        
        print("\n--- İLANLAR TARANIYOR ---\n")

        for link_tag in ilan_linkleri:
            # Sadece içinde 'search-results-row' olan a etiketlerini işleyelim
            row_div = link_tag.find("div", class_="search-results-row")
            
            if row_div:
                bulunan_ilan_sayisi += 1
                
                # Linki al
                ilan_url = base_url + link_tag['href']
                
                # Başlığı al (col-4 içindeki metin veya genel row içindeki metin analizi)
                # Yapıyı dinamik çözümlemek için:
                cols = row_div.find_all("div", class_="col")
                baslik = "Başlık Bulunamadı"
                
                # Genellikle 2. kolon başlıktır
                if len(cols) >= 2:
                    baslik = cols[1].get_text(strip=True)
                
                print(f"İLAN #{bulunan_ilan_sayisi}")
                print(f"Başlık: {baslik}")
                print(f"Link  : {ilan_url}")
                
                # Detay sayfasına git
                detay_cek(ilan_url, headers)
                
                print("-" * 50)
                
                # Test amaçlı sadece ilk 3 ilanı çekip duralım
                if bulunan_ilan_sayisi >= 3:
                    print("\nTest modu: İlk 3 ilan çekildi, işlem durduruluyor.")
                    break
                
                # Nezaketen bekleme
                time.sleep(2)

        if bulunan_ilan_sayisi == 0:
            print("UYARI: Hiç ilan bulunamadı. Site JavaScript (Angular) ile yükleniyor olabilir.")
            print("Bu durumda 'Selenium' kütüphanesine geçmemiz gerekecek.")

    except Exception as e:
        print(f"Kritik Hata: {e}")

def detay_cek(url, headers):
    print("  > Detay sayfasına gidiliyor...")
    try:
        res = requests.get(url, headers=headers, verify=False)
        detay_soup = BeautifulSoup(res.text, 'html.parser')
        
        # Detay metnini bulmaya çalışalım.
        # ilan.gov.tr genellikle metni 'ilan-detay-panel' veya 'content-body' içine koyar.
        # En garanti yol, olası içerik alanlarını taramaktır.
        
        icerik = ""
        
        # Olası içerik seçicileri
        selectors = [
            "div.content-body",
            "div#ilan-detay-icerik",
            "div.ilan-detay-aciklama",
            "div.ng-star-inserted" # Angular genelde bunu kullanır, biraz geniş bir seçimdir
        ]
        
        found = False
        for sel in selectors:
            # Sadece mantıklı uzunlukta metin içeren divleri al
            divs = detay_soup.select(sel)
            for div in divs:
                text = div.get_text(separator="\n", strip=True)
                if len(text) > 100: # Mantıklı bir içerik uzunluğu
                    icerik = text
                    found = True
                    break
            if found:
                break
        
        if not found:
            # Eğer spesifik div bulamazsak, genel body text'i alıp özetleyelim
            # print("  > (Not: Özel içerik div'i bulunamadı, genel metin alınıyor)")
            # Body içindeki script ve style'ları temizle
            for script in detay_soup(["script", "style"]):
                script.extract()
            icerik = detay_soup.get_text(separator="\n", strip=True)

        # Çıktıyı kısaltarak göster
        ozet = icerik[:200].replace('\n', ' ') + "..."
        print(f"  > İÇERİK ÖZETİ: {ozet}")
        
    except Exception as e:
        print(f"  > Detay çekilemedi: {e}")

if __name__ == "__main__":
    test_et()

