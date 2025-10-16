from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors

def create_seating_plan_pdf(file_path, plan_for_pdf, derslikler_info):
    """
    Verilen oturma planını, daha küçük öğrenci kutucukları kullanarak
    kompakt ve şık bir tasarımla PDF'e aktarır.
    """
    try:
        c = canvas.Canvas(file_path, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Renk Paleti
        renk_cerceve_belirgin = colors.HexColor('#757575')
        renk_cerceve = colors.HexColor('#B0BEC5')
        renk_kutu_ici = colors.white
        renk_baslik = colors.HexColor('#212121')
        renk_metin = colors.HexColor('#424242')
        renk_sira_no = colors.HexColor('#616161')

        derslik_sozluk = {
            derslik[0]: {"adi": derslik[1], "sira_yapisi": derslik[4]}
            for derslik in derslikler_info
        }

        derslik_planlari = {derslik_id: [] for derslik_id in derslik_sozluk}
        for atama in plan_for_pdf:
            if atama['derslik_id'] in derslik_planlari:
                derslik_planlari[atama['derslik_id']].append(atama)

        for derslik_id, ogrenciler in derslik_planlari.items():
            if not ogrenciler:
                continue

            derslik_bilgisi = derslik_sozluk[derslik_id]
            
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(renk_baslik)
            c.drawCentredString(width / 2, height - 1.5 * cm, f"{derslik_bilgisi['adi']} Sınav Oturma Planı")

            sira_yapisi = derslik_bilgisi.get('sira_yapisi', 'Tekli')
            if sira_yapisi == 'Dorderli': grup_boyutu = 4
            elif sira_yapisi == 'Üçerli': grup_boyutu = 3
            elif sira_yapisi == 'İkişerli': grup_boyutu = 2
            else: grup_boyutu = 1

            siradaki_ogrenciler = {}
            for ogrenci in ogrenciler:
                sira_no = ogrenci['sira_no']
                if sira_no not in siradaki_ogrenciler:
                    siradaki_ogrenciler[sira_no] = []
                siradaki_ogrenciler[sira_no].append(ogrenci)
            
            for sira_no in siradaki_ogrenciler:
                siradaki_ogrenciler[sira_no].sort(key=lambda x: x['sutun_no'])

            # --- YERLEŞİM AYARLARI (DAHA KÜÇÜK KUTUCUKLAR İÇİN GÜNCELLENDİ) ---
            x_offset = 2.5 * cm
            y_offset = height - 3 * cm
            sutun_boslugu = 3.4 * cm    # Sütun boşluğu azaltıldı
            satir_boslugu = 1.5 * cm    # Sıra boşluğu azaltıldı
            koltuk_genisligi = 3.0 * cm # Koltuk genişliği küçültüldü
            koltuk_yuksekligi = 1.0 * cm  # Koltuk yüksekliği küçültüldü
            cerceve_padding = 0.15 * cm
            kose_yuvarlakligi = 3

            for sira_no, ogrenciler_sirada in sorted(siradaki_ogrenciler.items()):
                if not ogrenciler_sirada:
                    continue

                sira_y_pozisyonu = y_offset - (sira_no - 1) * satir_boslugu + (koltuk_yuksekligi / 2) - (9/2)
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColor(renk_sira_no)
                c.drawString(1 * cm, sira_y_pozisyonu, f"SIRA {sira_no}")

                if grup_boyutu > 1:
                    c.setStrokeColor(renk_cerceve_belirgin)
                    c.setLineWidth(1.2)
                    c.setDash(5, 3)
                    
                    for i in range(0, len(ogrenciler_sirada), grup_boyutu):
                        grup = ogrenciler_sirada[i:i+grup_boyutu]
                        ilk_ogrenci = grup[0]
                        cerceve_x = x_offset + (ilk_ogrenci['sutun_no'] - 1) * sutun_boslugu - cerceve_padding
                        cerceve_y = y_offset - (sira_no - 1) * satir_boslugu - cerceve_padding
                        
                        mevcut_grup_boyutu = len(grup)
                        cerceve_genisligi = (mevcut_grup_boyutu * koltuk_genisligi) + \
                                            ((mevcut_grup_boyutu - 1) * (sutun_boslugu - koltuk_genisligi)) + \
                                            (2 * cerceve_padding)
                        cerceve_yuksekligi = koltuk_yuksekligi + (2 * cerceve_padding)

                        c.roundRect(cerceve_x, cerceve_y, cerceve_genisligi, cerceve_yuksekligi, kose_yuvarlakligi, stroke=1, fill=0)
                    
                    c.setDash([])
                    c.setLineWidth(1)

                for ogrenci in ogrenciler_sirada:
                    x = x_offset + (ogrenci['sutun_no'] - 1) * sutun_boslugu
                    y = y_offset - (ogrenci['sira_no'] - 1) * satir_boslugu
                    
                    c.setStrokeColor(renk_cerceve)
                    c.setFillColor(renk_kutu_ici)
                    c.roundRect(x, y, koltuk_genisligi, koltuk_yuksekligi, kose_yuvarlakligi, stroke=1, fill=1)
                    
                    # --- FONT VE METİN POZİSYONLARI KÜÇÜLEN KUTUYA GÖRE AYARLANDI ---
                    c.setFont("Helvetica-Bold", 7.5) # Font küçültüldü
                    c.setFillColor(renk_baslik)
                    c.drawString(x + 0.2 * cm, y + 0.6 * cm, str(ogrenci['ogrenci_no'])) # Pozisyon ayarlandı

                    c.setFont("Helvetica", 6.5) # Font küçültüldü
                    c.setFillColor(renk_metin)
                    c.drawString(x + 0.2 * cm, y + 0.2 * cm, ogrenci['ad_soyad'][:25]) # Pozisyon ayarlandı

            c.showPage()

        c.save()
        return True, "PDF dosyası başarıyla oluşturuldu."
    except Exception as e:
        return False, f"PDF oluşturulurken hata oluştu: {e}"