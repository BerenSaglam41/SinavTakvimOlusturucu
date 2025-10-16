import pandas as pd

def parse_ders_listesi(file_path):
    """
    Excel dosyasını okur ve her sınıfın altındaki dersleri listeler.
    Dersleri "Zorunlu", "Seçmeli" veya "Seçimlik" olarak doğru şekilde sınıflandırır.
    """
    print("--- Excel Parser Başlatıldı ---")
    print(f"Dosya Yolu: {file_path}")

    try:
        df = pd.read_excel(file_path, header=None)
        print(f"Toplam {len(df)} satır bulundu.\n")

        dersler_listesi = []
        current_sinif = None
        # Dersin yapısını (Zorunlu, Seçmeli, Seçimlik) izlemek için yeni bir değişken
        current_yapi = "Zorunlu"

        for index, row in df.iterrows():
            first_cell = str(row[0]).strip() if not pd.isnull(row[0]) else ""

            if not first_cell:
                continue  # Boş satırları atla

            # "SEÇMELİ DERS" veya "SEÇİMLİK DERS" başlıklarını yakala
            if "SEÇMELİ DERS" in first_cell.upper():
                current_yapi = "Seçmeli"
                print("-> 'Seçmeli Dersler' bölümü algılandı.")
                continue
            elif "SEÇİMLİK DERS" in first_cell.upper():
                current_yapi = "Seçimlik"
                print("-> 'Seçimlik Dersler' bölümü algılandı.")
                continue
            # "1. Sınıf", "2. Sınıf" gibi başlıkları yakala
            elif "SINIF" in first_cell.upper():
                for char in first_cell:
                    if char.isdigit():
                        current_sinif = int(char)
                        # Yeni bir sınıfa geçildiğinde, ders yapısını varsayılana (Zorunlu) döndür
                        current_yapi = "Zorunlu"
                        print(f"\n{current_sinif}. Sınıf algılandı (Ders yapısı '{current_yapi}' olarak ayarlandı).")
                        break
                continue

            # "DERS KODU" gibi başlık satırlarını atla
            if first_cell.upper() == "DERS KODU":
                continue

            # Ders satırları
            if current_sinif:
                ders_kodu = row[0]
                ders_adi = row[1]
                ogretim_uyesi = row[2] if len(row) > 2 else None
                
                # Ders bilgisi sözlüğünü oluştururken mevcut yapı bilgisini kullan
                ders_bilgisi = {
                    'ders_kodu': ders_kodu,
                    'ders_adi': ders_adi,
                    'ogretim_uyesi': ogretim_uyesi,
                    'yapi': current_yapi, # Düzeltilmiş kısım
                    'sinif': current_sinif
                }

                dersler_listesi.append(ders_bilgisi)
                print(f"{current_sinif}. Sınıfa eklendi: {ders_bilgisi}")
            else:
                print(f"Henüz sınıf başlığı tespit edilmeden veri bulundu (satır {index+1}).")

        print(f"\n--- Tamamlandı: {len(dersler_listesi)} ders bulundu. ---")

        if not dersler_listesi:
            return False, "Hiçbir ders bulunamadı. Dosya formatını kontrol et."

        return True, dersler_listesi

    except FileNotFoundError:
        return False, "Dosya bulunamadı."
    except Exception as e:
        return False, f"Hata: {e}"

def parse_ogrenci_listesi(file_path):
    """
    Öğrenci listesi Excel dosyasını okur ve veritabanına eklenebilecek
    bir formatta (sözlük listesi) döndürür.
    """
    try:
        df = pd.read_excel(file_path)

        # Sütun isimlerini normalize et (boşluk, büyük/küçük farkı, Türkçe karakter vs.)
        df.columns = df.columns.str.strip().str.lower().str.replace("ö", "o").str.replace("ü", "u").str.replace("ı", "i").str.replace("ş", "s").str.replace("ç", "c").str.replace("ğ", "g")

        # Eski -> Yeni sütun isim eşlemesi
        sutun_map = {
            'ogrenci no': 'ogrenci_no',
            'ad soyad': 'ad_soyad',
            'sinif': 'sinif',
            'ders': 'ders_kodu'  # senin dosyanda "Ders" sütunu ders kodunu temsil ediyor
        }

        # Sadece mevcut sütunları yeniden adlandır
        df.rename(columns={k: v for k, v in sutun_map.items() if k in df.columns}, inplace=True)

        # Gerekli sütunların mevcut olup olmadığını kontrol et
        gerekli_sutunlar = ['ogrenci_no', 'ad_soyad', 'sinif', 'ders_kodu']
        eksikler = [s for s in gerekli_sutunlar if s not in df.columns]
        if eksikler:
            return False, f"Excel dosyasında eksik sütun(lar) var: {', '.join(eksikler)}"

        # Boş satırları temizle
        df.dropna(subset=['ogrenci_no', 'ders_kodu'], inplace=True)

        # Gereksiz boşlukları temizle
        df['ogrenci_no'] = df['ogrenci_no'].astype(str).str.strip()
        df['ad_soyad'] = df['ad_soyad'].astype(str).str.strip()
        df['sinif'] = df['sinif'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
        df['ders_kodu'] = df['ders_kodu'].astype(str).str.strip()

        kayitlar_listesi = df.to_dict('records')

        print(f"Toplam {len(kayitlar_listesi)} öğrenci kaydı bulundu.")
        return True, kayitlar_listesi

    except FileNotFoundError:
        return False, "Dosya bulunamadı."
    except Exception as e:
        return False, f"Excel dosyası okunurken bir hata oluştu: {e}"