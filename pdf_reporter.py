from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm


def create_seating_plan_pdf(file_path, plan_for_pdf, derslikler_info):
    """Verilen oturma planını bir PDF dosyasına çizer."""
    try:
        c = canvas.Canvas(file_path, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Derslikleri grupla
        derslik_planlari = {}
        for derslik_id, derslik_adi, _, _, _ in derslikler_info:
            derslik_planlari[derslik_id] = {"adi": derslik_adi, "ogrenciler": []}

        for atama in plan_for_pdf:
            derslik_planlari[atama['derslik_id']]['ogrenciler'].append(atama)

        for derslik_id, data in derslik_planlari.items():
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - 1.5 * cm, f"Oturma Planı - {data['adi']}")

            c.setFont("Helvetica", 8)
            x_offset = 2 * cm
            y_offset = height - 3 * cm

            for ogrenci in data['ogrenciler']:
                sutun_boslugu = 3.5 * cm
                satir_boslugu = 1 * cm

                x = x_offset + (ogrenci['sutun_no'] - 1) * sutun_boslugu
                y = y_offset - (ogrenci['sira_no'] - 1) * satir_boslugu

                c.rect(x, y, 3 * cm, 0.8 * cm)  # Koltuk kutusu
                c.drawString(x + 0.2 * cm, y + 0.5 * cm, str(ogrenci['ogrenci_no']))
                c.drawString(x + 0.2 * cm, y + 0.2 * cm, ogrenci['ad_soyad'][:20])  # İsim çok uzunsa kırp

            c.showPage()  # Her derslik için yeni bir sayfa

        c.save()
        return True, "PDF dosyası başarıyla oluşturuldu."
    except Exception as e:
        return False, f"PDF oluşturulurken hata oluştu: {e}"