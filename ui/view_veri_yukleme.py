# ui/view_veri_yukleme.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal
import excel_parser
import database

class VeriYuklemeView(QWidget):
    # Yükleme tamamlandığında ana pencereye sinyal göndermek için
    veri_yuklendi_sinyali = pyqtSignal(str) # 'ders' veya 'ogrenci'

    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info

        layout = QVBoxLayout(self)

        self.ders_yukle_button = QPushButton("Ders Listesi Yükle (Excel)")
        self.ogrenci_yukle_button = QPushButton("Öğrenci Listesi Yükle (Excel)")

        layout.addWidget(QLabel("Lütfen ilgili Excel dosyalarını sisteme yükleyiniz:"))
        layout.addWidget(self.ders_yukle_button)
        layout.addWidget(self.ogrenci_yukle_button)
        layout.addStretch()

        self.ders_yukle_button.clicked.connect(self.ders_listesi_yukle)
        self.ogrenci_yukle_button.clicked.connect(self.ogrenci_listesi_yukle)
        # self.ogrenci_yukle_button.clicked.connect(self.ogrenci_listesi_yukle)

    def ders_listesi_yukle(self):
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            QMessageBox.warning(self, "Hata", "Bu işlem için Bölüm Koordinatörü olarak giriş yapmalısınız.")
            return

        # Dosya seçme penceresini aç
        file_path, _ = QFileDialog.getOpenFileName(self, "Ders Listesi Excel Dosyasını Seçin", "", "Excel Dosyaları (*.xlsx *.xls)")

        if file_path:
            basarili, sonuc = excel_parser.parse_ders_listesi(file_path)

            if not basarili:
                QMessageBox.critical(self, "Excel Okuma Hatası", sonuc)
                return

            basarili_db, mesaj_db = database.dersleri_sil_ve_ekle(sonuc, bolum_id)

            if basarili_db:
                QMessageBox.information(self, "Başarılı", mesaj_db)
                self.veri_yuklendi_sinyali.emit('ders') # Ana pencereye sinyal gönder
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", mesaj_db)

    def ogrenci_listesi_yukle(self):
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            QMessageBox.warning(self, "Hata", "Bu işlem için Bölüm Koordinatörü olarak giriş yapmalısınız.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Öğrenci Listesi Excel Dosyasını Seçin", "",
                                                   "Excel Dosyaları (*.xlsx *.xls)")

        if file_path:
            basarili, sonuc = excel_parser.parse_ogrenci_listesi(file_path)

            if not basarili:
                QMessageBox.critical(self, "Excel Okuma Hatası", sonuc)
                return

            basarili_db, mesaj_db = database.ogrencileri_sil_ve_ekle(sonuc, bolum_id)

            if basarili_db:
                QMessageBox.information(self, "Başarılı", mesaj_db)
                self.veri_yuklendi_sinyali.emit('ogrenci')  # Ana pencereye sinyal gönder
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", mesaj_db)