import database
from datetime import date, timedelta, datetime, time
import pandas as pd # Dosyanın en üstüne bu importu ekle
import itertools
import random
def _verileri_hazirla(bolum_id, secilen_ders_idler):
    print("Algoritma için veriler hazırlanıyor...")
    dersler = {}
    ogrenci_dersleri = {}
    derslikler = []
    ders_ogrencileri = {}
    conn = None
    try:
        conn = database.get_connection()
        cur = conn.cursor()
        dersler_sql = """
                      SELECT d.ders_id, d.ders_kodu, d.ders_adi, d.sinif, COUNT(odk.ogrenci_id) as ogrenci_sayisi
                      FROM Dersler d
                               LEFT JOIN OgrenciDersKayitlari odk ON d.ders_id = odk.ders_id
                      WHERE d.bolum_id = %s \
                        AND d.ders_id = ANY (%s)
                      GROUP BY d.ders_id, d.ders_kodu, d.ders_adi, d.sinif; \
                      """
        cur.execute(dersler_sql, (bolum_id, secilen_ders_idler))
        for row in cur.fetchall():
            dersler[row[0]] = {'kod': row[1], 'ad': row[2], 'sinif': row[3], 'ogrenci_sayisi': row[4]}
            ders_ogrencileri[row[0]] = set()
        print(f"-> {len(dersler)} adet ders bilgisi alındı.")
        ogrenci_dersleri_sql = """
                               SELECT odk.ogrenci_id, odk.ders_id
                               FROM OgrenciDersKayitlari odk
                                        JOIN Ogrenciler o ON odk.ogrenci_id = o.ogrenci_id
                               WHERE o.bolum_id = %s; \
                               """
        cur.execute(ogrenci_dersleri_sql, (bolum_id,))
        for ogrenci_id, ders_id in cur.fetchall():
            if ogrenci_id not in ogrenci_dersleri:
                ogrenci_dersleri[ogrenci_id] = set()
            ogrenci_dersleri[ogrenci_id].add(ders_id)
            if ders_id in ders_ogrencileri:
                ders_ogrencileri[ders_id].add(ogrenci_id)
        print(f"-> {len(ogrenci_dersleri)} öğrencinin ve derslerin kayıtları çakışma kontrolü için alındı.")
        derslikler_sql = "SELECT derslik_id, derslik_adi, kapasite FROM Derslikler WHERE bolum_id = %s ORDER BY kapasite DESC;"
        cur.execute(derslikler_sql, (bolum_id,))
        for row in cur.fetchall():
            derslikler.append({'id': row[0], 'ad': row[1], 'kapasite': row[2]})
        print(f"-> {len(derslikler)} adet derslik bilgisi alındı.")
        cur.close()
        return dersler, ogrenci_dersleri, derslikler, ders_ogrencileri
    except Exception as e:
        print(f"Veri hazırlama sırasında HATA: {e}")
        return None, None, None, None
    finally:
        if conn is not None:
            conn.close()

def _zaman_dilimlerini_olustur(ayarlar):
    print("Sınav yapılabilecek zaman dilimleri oluşturuluyor...")
    baslangic = datetime.strptime(ayarlar['baslangic_tarihi'], "%Y-%m-%d").date()
    bitis = datetime.strptime(ayarlar['bitis_tarihi'], "%Y-%m-%d").date()
    gecerli_gunler = ayarlar['gecerli_gunler']
    zaman_dilimleri = []
    mevcut_tarih = baslangic
    while mevcut_tarih <= bitis:
        if mevcut_tarih.weekday() in gecerli_gunler:
            sinav_saati = time(9, 0)
            gun_bitis_saati = time(17, 0)
            while sinav_saati < gun_bitis_saati:
                slot = datetime.combine(mevcut_tarih, sinav_saati)
                zaman_dilimleri.append(slot)
                toplam_gecen_sure = ayarlar['varsayilan_sure'] + ayarlar['mola_suresi']
                yeni_saat_dt = datetime.combine(date.today(), sinav_saati) + timedelta(minutes=toplam_gecen_sure)
                sinav_saati = yeni_saat_dt.time()
        mevcut_tarih += timedelta(days=1)
    print(f"-> Toplam {len(zaman_dilimleri)} adet sınav zaman dilimi (slot) oluşturuldu.")
    return zaman_dilimleri

def _uygun_derslik_bul(ders_ogrenci_sayisi, kullanilabilir_derslikler):
    """
    (AKILLI SÜRÜM 3.0) Verilen öğrenci sayısı için, kapasiteyi karşılayan
    ve derslik kullanımını çeşitlendiren verimli bir kombinasyon bulur.
    """
    if not kullanilabilir_derslikler:
        return None

    # --- ÇEŞİTLİLİĞİ SAĞLAYAN YENİ ADIM ---
    # Kombinasyonları aramadan önce mevcut boş derslik listesini karıştır.
    # Bu, her seferinde farklı bir arama sırası oluşturur ve
    # aynı dersliklerin tekrar tekrar seçilmesini engeller.
    random.shuffle(kullanilabilir_derslikler)
    # ------------------------------------

    # 1'den başlayarak tüm olası kombinasyon boyutlarını dene
    for i in range(1, len(kullanilabilir_derslikler) + 1):
        for kombinasyon in itertools.combinations(kullanilabilir_derslikler, i):
            toplam_kapasite = sum(d['kapasite'] for d in kombinasyon)

            # Eğer bu kombinasyonun kapasitesi yeterliyse, hemen döndür.
            # Liste zaten rastgele olduğu için, bu yeterli kapasiteyi sağlayan
            # ilk geçerli kombinasyon olacaktır.
            if toplam_kapasite >= ders_ogrenci_sayisi:
                return list(kombinasyon)

    # Yeterli kapasite bulunamadıysa
    return None

def program_olustur(bolum_id, ayarlar, secilen_ders_idler):
    """
    (HATA AYIKLAMA SÜRÜMÜ) Algoritmanın her adımını terminale yazdırır.
    """
    # ... (fonksiyonun başındaki veri hazırlama ve zaman dilimi oluşturma kısımları aynı) ...
    dersler, ogrenci_dersleri, tum_derslikler, ders_ogrencileri = _verileri_hazirla(bolum_id, secilen_ders_idler)
    if dersler is None: return False, "Veritabanından veri hazırlanırken bir hata oluştu."
    zaman_dilimleri = _zaman_dilimlerini_olustur(ayarlar)
    if not zaman_dilimleri: return False, "Belirtilen tarih aralığı ve günlerde hiç uygun sınav zamanı bulunamadı."
    sirali_dersler = sorted(dersler.items(), key=lambda item: item[1]['ogrenci_sayisi'], reverse=True)
    planlanan_sinavlar = {slot: {'dersler': [], 'kullanilan_derslik_idler': set()} for slot in zaman_dilimleri}
    sinav_programi = {}

    print("\n--- Yerleştirme Algoritması Başlatıldı (Detaylı Raporlama Aktif) ---")
    for ders_id, ders_info in sirali_dersler:
        yerlestirildi = False
        print(f"\n[DERS]: {ders_info['kod']} ({ders_info['ogrenci_sayisi']} öğrenci) için yer aranıyor...")

        for slot in zaman_dilimleri:
            # a) Öğrenci Çakışma Kontrolü
            slot_ogrencileri = set()
            for slot_ders_id in planlanan_sinavlar[slot]['dersler']:
                slot_ogrencileri.update(ders_ogrencileri[slot_ders_id])

            yeni_ders_ogrencileri = ders_ogrencileri[ders_id]
            if not slot_ogrencileri.isdisjoint(yeni_ders_ogrencileri):
                print(f"  -> [SLOT ATLANDI] {slot.strftime('%d.%m %H:%M')}: Öğrenci Çakışması.")
                continue  # Bu slotu atla

            # b) Derslik Kapasite ve Uygunluk Kontrolü
            kullanilan_idler = planlanan_sinavlar[slot]['kullanilan_derslik_idler']
            kullanilabilir_derslikler = [d for d in tum_derslikler if d['id'] not in kullanilan_idler]

            atanan_derslikler = _uygun_derslik_bul(ders_info['ogrenci_sayisi'], kullanilabilir_derslikler)

            if atanan_derslikler is None:
                print(f"  -> [SLOT ATLANDI] {slot.strftime('%d.%m %H:%M')}: Yetersiz Derslik Kapasitesi.")
                continue  # Bu slotu atla

            # c) Yerleştirme Başarılı
            planlanan_sinavlar[slot]['dersler'].append(ders_id)
            atanan_idler = {d['id'] for d in atanan_derslikler}
            planlanan_sinavlar[slot]['kullanilan_derslik_idler'].update(atanan_idler)
            sinav_programi[ders_id] = {'tarih': slot.date(), 'saat': slot.time(), 'derslikler': atanan_derslikler,
                                       'ders_info': ders_info}
            print(
                f"  -> [BAŞARILI] {slot.strftime('%d.%m.%Y %H:%M')} -> Derslikler: {[d['ad'] for d in atanan_derslikler]}")
            yerlestirildi = True
            break

        if not yerlestirildi:
            print(f"  -> [HATA] Bu ders için denenen tüm slotlar başarısız oldu.")
            return False, f"'{ders_info['kod']}' dersi için uygun bir zaman veya derslik bulunamadı! Lütfen tarih aralığını genişletin, derslikleri kontrol edin veya daha az ders seçin."

    print("--- Algoritma Başarıyla Tamamlandı ---")
    return True, sinav_programi

def programi_excele_aktar(program, dosya_yolu):
    """Oluşturulan sınav programını bir Excel dosyasına aktarır."""
    try:
        data_for_excel = []
        for ders_id, info in program.items():
            derslik_adlari = ", ".join([d['ad'] for d in info['derslikler']])
            data_for_excel.append({
                "Tarih": info['tarih'].strftime('%d.%m.%Y'),
                "Sınav Saati": info['saat'].strftime('%H:%M'),
                "Ders Kodu": info['ders_info']['kod'],
                "Ders Adı": info['ders_info']['ad'],
                "Derslikler": derslik_adlari
            })

        df = pd.DataFrame(data_for_excel)
        df.sort_values(by=["Tarih", "Sınav Saati"], inplace=True)  # Tarih ve saate göre sırala
        df.to_excel(dosya_yolu, index=False)
        return True, f"Program başarıyla '{dosya_yolu}' dosyasına kaydedildi."
    except Exception as e:
        return False, f"Excel dosyası oluşturulurken hata oluştu: {e}"