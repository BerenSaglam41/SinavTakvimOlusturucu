import random

def generate_seating_plan(sinav_id, ogrenciler, derslikler):
    """
    Verilen öğrenciler ve derslikler için basit bir oturma planı oluşturur.
    Öğrencileri dersliklere sırayla yerleştirir.
    """
    print("Oturma planı algoritması başlatıldı...")

    tum_koltuklar = []
    for derslik in derslikler:
        derslik_id, derslik_adi, enine_sira, boyuna_sira, sira_yapisi = derslik
        for satir in range(boyuna_sira):
            for sutun in range(enine_sira):
                tum_koltuklar.append({
                    "derslik_id": derslik_id,
                    "derslik_adi": derslik_adi,
                    "sira_no": satir + 1,
                    "sutun_no": sutun + 1
                })
    print(f"-> Toplam {len(tum_koltuklar)} adet koltuk bulundu.")
    print(f"-> Toplam {len(ogrenciler)} öğrenci yerleştirilecek.")

    if len(ogrenciler) > len(tum_koltuklar):
        return False, "HATA: Öğrenci sayısı, dersliklerdeki toplam koltuk sayısından fazla!", None, None

    random.shuffle(ogrenciler)

    plan = []
    plan_for_pdf = []
    for i, ogrenci in enumerate(ogrenciler):
        ogrenci_id, ogrenci_no, ad_soyad = ogrenci
        atanan_koltuk = tum_koltuklar[i]

        # --- DEĞİŞİKLİK BURADA: TUPLE'A sinav_id EKLENDİ ---
        # Veritabanına kaydetmek için veri (Artık 5 elemanlı)
        plan.append((
            sinav_id,  # 1. Eleman (YENİ)
            ogrenci_id,  # 2. Eleman
            atanan_koltuk["derslik_id"],  # 3. Eleman
            atanan_koltuk["sira_no"],  # 4. Eleman
            atanan_koltuk["sutun_no"]  # 5. Eleman
        ))

        plan_for_pdf.append({
            "ogrenci_id": ogrenci_id,
            "ogrenci_no": ogrenci_no,
            "ad_soyad": ad_soyad,
            **atanan_koltuk
        })

    print("-> Öğrenciler koltuklara başarıyla atandı.")
    return True, "Plan başarıyla oluşturuldu.", plan, plan_for_pdf