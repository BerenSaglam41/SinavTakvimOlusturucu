from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QMessageBox)
import database
from PyQt6.QtWidgets import QFileDialog
import oturma_plani_algoritmasi
import pdf_reporter


class OturmaPlaniView(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(QLabel("Oturma planını oluşturmak için aşağıdan bir sınav seçin:"))

        self.sinav_listesi_widget = QListWidget()
        main_layout.addWidget(self.sinav_listesi_widget)

        self.olustur_button = QPushButton("Seçili Sınav İçin Oturma Planı Oluştur ve Göster")
        self.olustur_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.olustur_button.clicked.connect(self.oturma_plani_olustur)
        main_layout.addWidget(self.olustur_button)

    def load_data(self):
        """Bu sayfa açıldığında, oluşturulmuş sınavların listesini veritabanından yükler."""
        self.sinav_listesi_widget.clear()
        sinavlar = database.get_sinav_listesi(self.user_info.get('bolum_id'))
        for sinav_id, ders_kodu, ders_adi, tarih, saat in sinavlar:
            # Tarih ve saat formatını daha okunaklı yapalım
            tarih_str = tarih.strftime('%d.%m.%Y')
            saat_str = saat.strftime('%H:%M')
            item_text = f"[{ders_kodu}] {ders_adi}  -  ({tarih_str} {saat_str})"

            self.sinav_listesi_widget.addItem(item_text)
            # Her bir elemana görünmez bir şekilde sinav_id'yi saklayalım
            self.sinav_listesi_widget.item(self.sinav_listesi_widget.count() - 1).setData(32, sinav_id)  # 32: UserRole

    def oturma_plani_olustur(self):
        """Butona basıldığında seçili sınav için plan oluşturur, kaydeder ve PDF'e aktarır."""
        secili_item = self.sinav_listesi_widget.currentItem()
        if not secili_item:
            QMessageBox.warning(self, "Hata", "Lütfen listeden bir sınav seçin.")
            return

        secili_sinav_id = secili_item.data(32)

        # 1. Adım: Veritabanından sınav detaylarını al
        ogrenciler, derslikler = database.get_sinav_detaylari_for_plan(secili_sinav_id)
        if not ogrenciler or not derslikler:
            QMessageBox.critical(self, "Hata", "Bu sınav için öğrenci veya derslik bilgisi bulunamadı.")
            return

        # 2. Adım: Oturma planı algoritmasını çalıştır (DÜZELTİLMİŞ SATIR)
        basarili_alg, mesaj_alg, plan_db, plan_pdf = oturma_plani_algoritmasi.generate_seating_plan(secili_sinav_id,
                                                                                                    ogrenciler,
                                                                                                    derslikler)
        if not basarili_alg:
            QMessageBox.critical(self, "Algoritma Hatası", mesaj_alg)
            return

        # 3. Adım: Planı veritabanına kaydet
        basarili_db, mesaj_db = database.oturma_planini_kaydet(secili_sinav_id, plan_db)
        if not basarili_db:
            QMessageBox.critical(self, "Veritabanı Kayıt Hatası", mesaj_db)
            return

        # 4. Adım: PDF olarak kaydet
        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "Oturma Planını Kaydet",
                                                    f"oturma_plani_{secili_sinav_id}.pdf", "PDF Dosyaları (*.pdf)")
        if dosya_yolu:
            basarili_pdf, mesaj_pdf = pdf_reporter.create_seating_plan_pdf(dosya_yolu, plan_pdf, derslikler)
            if not basarili_pdf:
                QMessageBox.critical(self, "PDF Oluşturma Hatası", mesaj_pdf)
                return

            QMessageBox.information(self, "Başarılı!", f"{mesaj_db}\n{mesaj_pdf}")
        else:
            QMessageBox.information(self, "Başarılı!",
                                    f"{mesaj_db}\nPDF kaydetme işlemi kullanıcı tarafından iptal edildi.")