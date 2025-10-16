from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QGroupBox, QFormLayout, QDateEdit,
    QComboBox, QSpinBox, QListWidget, QListWidgetItem, QCheckBox, QFileDialog
)
from PyQt6.QtCore import QDate, Qt, pyqtSignal
import database
import takvim_algoritmasi

class SinavOlusturmaView(QWidget):
    program_basariyla_olusturuldu = pyqtSignal()
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
            }
            QGroupBox {
                font-size: 16px;
                color: #007AFF;
                border: 2px solid #dde2ec;
                border-radius: 13px;
                margin-top: 16px;
            }
            QDateEdit, QComboBox, QSpinBox {
                background: rgba(245,245,247,0.9);
                border-radius: 10px;
                border: 1.5px solid #dde2ec;
                padding: 7px 10px;
                font-size: 15px;
            }
            QCheckBox {
                font-size: 15px;
                color: #3245FF;
                spacing: 12px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #007AFF, stop:1 #3A86FF);
                color: #fff;
                font-size: 16px;
                font-weight: 600;
                border: none;
                border-radius: 12px;
                padding: 10px 0;
                margin-top: 16px;
            }
            QPushButton:hover { background: #005bb5; }
            QListWidget {
                background: #fff;
                border-radius: 10px;
                border: 1.3px solid #dde2ec;
                font-size: 15px;
                color: #21283d;
                padding: 6px;
            }
        """)

        main_layout = QHBoxLayout(self)
        # --- Sol Taraf: Ayarlar ve Kısıtlar ---
        sol_taraf_layout = QVBoxLayout()

        tarih_group = QGroupBox("Tarih ve Gün Kısıtları")
        tarih_layout_dis = QVBoxLayout(tarih_group)
        tarih_form = QFormLayout()
        self.tarih_baslangic = QDateEdit(QDate.currentDate())
        self.tarih_baslangic.setCalendarPopup(True)
        self.tarih_bitis = QDateEdit(QDate.currentDate().addDays(14))
        self.tarih_bitis.setCalendarPopup(True)
        tarih_form.addRow("Sınav Başlangıç Tarihi:", self.tarih_baslangic)
        tarih_form.addRow("Sınav Bitiş Tarihi:", self.tarih_bitis)

        gunler_group = QGroupBox("Sınav Yapılacak Günler")
        gunler_layout = QHBoxLayout(gunler_group)
        self.gun_pazartesi = QCheckBox("Pazartesi"); self.gun_pazartesi.setChecked(True)
        self.gun_sali = QCheckBox("Salı"); self.gun_sali.setChecked(True)
        self.gun_carsamba = QCheckBox("Çarşamba"); self.gun_carsamba.setChecked(True)
        self.gun_persembe = QCheckBox("Perşembe"); self.gun_persembe.setChecked(True)
        self.gun_cuma = QCheckBox("Cuma"); self.gun_cuma.setChecked(True)
        self.gun_cumartesi = QCheckBox("Cumartesi"); self.gun_cumartesi.setChecked(False)
        self.gun_pazar = QCheckBox("Pazar"); self.gun_pazar.setChecked(False)
        gunler_layout.addWidget(self.gun_pazartesi)
        gunler_layout.addWidget(self.gun_sali)
        gunler_layout.addWidget(self.gun_carsamba)
        gunler_layout.addWidget(self.gun_persembe)
        gunler_layout.addWidget(self.gun_cuma)
        gunler_layout.addWidget(self.gun_cumartesi)
        gunler_layout.addWidget(self.gun_pazar)
        tarih_layout_dis.addLayout(tarih_form)
        tarih_layout_dis.addWidget(gunler_group)

        sinav_ayarlari_group = QGroupBox("Genel Sınav Ayarları")
        sinav_ayarlari_form = QFormLayout(sinav_ayarlari_group)
        self.sinav_turu = QComboBox(); self.sinav_turu.addItems(["Vize", "Final", "Bütünleme"])
        self.varsayilan_sure = QSpinBox(); self.varsayilan_sure.setRange(30, 180); self.varsayilan_sure.setValue(75); self.varsayilan_sure.setSuffix(" dk")
        self.mola_suresi = QSpinBox(); self.mola_suresi.setRange(10, 60); self.mola_suresi.setValue(15); self.mola_suresi.setSuffix(" dk")
        sinav_ayarlari_form.addRow("Sınav Türü:", self.sinav_turu)
        sinav_ayarlari_form.addRow("Varsayılan Sınav Süresi:", self.varsayilan_sure)
        sinav_ayarlari_form.addRow("Sınav Arası Bekleme Süresi:", self.mola_suresi)

        self.olustur_button = QPushButton("Sınav Programını Oluştur")
        self.olustur_button.clicked.connect(self.program_olustur_baslat)

        sol_taraf_layout.addWidget(tarih_group)
        sol_taraf_layout.addWidget(sinav_ayarlari_group)
        sol_taraf_layout.addStretch()
        sol_taraf_layout.addWidget(self.olustur_button)

        # --- Sağ Taraf: Programa Dahil Edilecek Dersler ---
        sag_taraf_layout = QVBoxLayout()
        sag_taraf_layout.addWidget(QLabel("Programa Dahil Edilecek Dersleri Seçin:"))
        self.ders_listesi_widget = QListWidget()
        sag_taraf_layout.addWidget(self.ders_listesi_widget)
        main_layout.addLayout(sol_taraf_layout, 1)
        main_layout.addLayout(sag_taraf_layout, 2)

    def load_data(self):
        self.ders_listesi_widget.clear()
        dersler = database.bolumun_derslerini_getir(self.user_info.get('bolum_id'))
        for ders_id, ders_kodu, ders_adi in dersler:
            item_text = f"{ders_kodu} - {ders_adi}"
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.ItemDataRole.UserRole, ders_id)
            list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            list_item.setCheckState(Qt.CheckState.Checked)
            self.ders_listesi_widget.addItem(list_item)

    def program_olustur_baslat(self):
        secilen_ders_idler = [
            self.ders_listesi_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.ders_listesi_widget.count())
            if self.ders_listesi_widget.item(i).checkState() == Qt.CheckState.Checked
        ]
        if not secilen_ders_idler:
            QMessageBox.warning(self, "Hata", "Programa dahil edilecek en az bir ders seçmelisiniz."); return

        gecerli_gunler = [
            i for i, cb in enumerate(
                [self.gun_pazartesi, self.gun_sali, self.gun_carsamba, self.gun_persembe,
                 self.gun_cuma, self.gun_cumartesi, self.gun_pazar]) if cb.isChecked()
        ]
        if not gecerli_gunler:
            QMessageBox.warning(self, "Hata", "Sınav yapılacak en az bir gün seçmelisiniz."); return

        ayarlar = {
            "baslangic_tarihi": self.tarih_baslangic.date().toString("yyyy-MM-dd"),
            "bitis_tarihi": self.tarih_bitis.date().toString("yyyy-MM-dd"),
            "sinav_turu": self.sinav_turu.currentText(),
            "varsayilan_sure": self.varsayilan_sure.value(),
            "mola_suresi": self.mola_suresi.value(),
            "gecerli_gunler": gecerli_gunler
        }
        bolum_id = self.user_info.get('bolum_id')

        basarili, sonuc = takvim_algoritmasi.program_olustur(bolum_id, ayarlar, secilen_ders_idler)
        if basarili:
            sinav_turu = ayarlar['sinav_turu']
            db_basarili, db_mesaj = database.sinav_programini_kaydet(sonuc, bolum_id, sinav_turu)
            if not db_basarili:
                QMessageBox.critical(self, "Veritabanı Kayıt Hatası", db_mesaj); return
            dosya_yolu, _ = QFileDialog.getSaveFileName(
                self, "Sınav Programını Kaydet", "sinav_programi.xlsx", "Excel Dosyaları (*.xlsx)")
            excel_mesaj = "Excel'e aktarma işlemi kullanıcı tarafından iptal edildi."
            if dosya_yolu:
                excel_basarili, excel_mesaj = takvim_algoritmasi.programi_excele_aktar(sonuc, dosya_yolu)
                if not excel_basarili:
                    QMessageBox.critical(self, "Excel Aktarma Hatası", excel_mesaj); return
            QMessageBox.information(self, "Başarılı!", f"{db_mesaj}\n{excel_mesaj}")
            self.program_basariyla_olusturuldu.emit()
        else:
            QMessageBox.critical(self, "Algoritma Başarısız!", sonuc)
