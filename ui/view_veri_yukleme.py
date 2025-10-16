from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal
import excel_parser
import database

class VeriYuklemeView(QWidget):
    veri_yuklendi_sinyali = pyqtSignal(str)

    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info

        self.setStyleSheet("""
            QWidget {
                background: #F5F5F7;
                font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                font-size: 15px;
            }
            QLabel {
                font-size: 16px;
                color: #1A202C;
                font-weight: 600;
                margin-bottom: 5px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #007AFF, stop:1 #3A86FF);
                color: #fff;
                font-size: 16px;
                font-weight: 600;
                border: none;
                border-radius: 12px;
                padding: 12px 0;
                margin-bottom: 8px;
            }
            QPushButton:hover { background: #005bb5; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 22)
        layout.setSpacing(16)

        self.ders_yukle_button = QPushButton("Ders Listesi Yükle (Excel)")
        self.ogrenci_yukle_button = QPushButton("Öğrenci Listesi Yükle (Excel)")

        layout.addWidget(QLabel("Lütfen ilgili Excel dosyalarını sisteme yükleyiniz:"))
        layout.addWidget(self.ders_yukle_button)
        layout.addWidget(self.ogrenci_yukle_button)
        layout.addStretch()

        self.ders_yukle_button.clicked.connect(self.ders_listesi_yukle)
        self.ogrenci_yukle_button.clicked.connect(self.ogrenci_listesi_yukle)

    def ders_listesi_yukle(self):
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            QMessageBox.warning(self, "Hata", "Bu işlem için Bölüm Koordinatörü olarak giriş yapmalısınız.")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ders Listesi Excel Dosyasını Seçin", "", "Excel Dosyaları (*.xlsx *.xls)")
        if file_path:
            basarili, sonuc = excel_parser.parse_ders_listesi(file_path)
            if not basarili:
                QMessageBox.critical(self, "Excel Okuma Hatası", sonuc)
                return
            basarili_db, mesaj_db = database.dersleri_sil_ve_ekle(sonuc, bolum_id)
            if basarili_db:
                QMessageBox.information(self, "Başarılı", mesaj_db)
                self.veri_yuklendi_sinyali.emit('ders')
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", mesaj_db)

    def ogrenci_listesi_yukle(self):
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            QMessageBox.warning(self, "Hata", "Bu işlem için Bölüm Koordinatörü olarak giriş yapmalısınız.")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Öğrenci Listesi Excel Dosyasını Seçin", "", "Excel Dosyaları (*.xlsx *.xls)")
        if file_path:
            basarili, sonuc = excel_parser.parse_ogrenci_listesi(file_path)
            if not basarili:
                QMessageBox.critical(self, "Excel Okuma Hatası", sonuc)
                return
            basarili_db, mesaj_db = database.ogrencileri_sil_ve_ekle(sonuc, bolum_id)
            if basarili_db:
                QMessageBox.information(self, "Başarılı", mesaj_db)
                self.veri_yuklendi_sinyali.emit('ogrenci')
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", mesaj_db)
