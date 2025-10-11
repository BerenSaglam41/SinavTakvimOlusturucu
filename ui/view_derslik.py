# Yeni importları en üste ekleyin
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFormLayout, QSpinBox, QComboBox, QMessageBox, QGroupBox)
import database
from ui.gorsellestirme_dialog import GorsellestirmeDialog  # Yeni oluşturduğumuz pencereyi import et


class DerslikView(QWidget):
    def __init__(self, user_info):
        super().__init__()
        # ... (init fonksiyonunun başındaki değişkenler aynı) ...
        self.user_info = user_info
        self.secili_derslik_id = None

        main_layout = QHBoxLayout(self)

        # --- Sol Taraf: Giriş Formu ---
        # ... (Bu kısım tamamen aynı, değişiklik yok) ...
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_container.setFixedWidth(350)
        self.derslik_kodu_input = QLineEdit()
        self.derslik_adi_input = QLineEdit()
        self.kapasite_input = QSpinBox()
        self.kapasite_input.setRange(10, 200)
        self.enine_sira_input = QSpinBox()
        self.enine_sira_input.setRange(1, 20)
        self.boyuna_sira_input = QSpinBox()
        self.boyuna_sira_input.setRange(1, 20)
        self.sira_yapisi_input = QComboBox()
        self.sira_yapisi_input.addItems(["İkişerli", "Üçerli", "Tekli","Dorderli"])
        form_layout.addRow("Derslik Kodu:", self.derslik_kodu_input)
        form_layout.addRow("Derslik Adı:", self.derslik_adi_input)
        form_layout.addRow("Kapasite:", self.kapasite_input)
        form_layout.addRow("Enine Sıra Sayısı (Sütun):", self.enine_sira_input)
        form_layout.addRow("Boyuna Sıra Sayısı (Satır):", self.boyuna_sira_input)
        form_layout.addRow("Sıra Yapısı:", self.sira_yapisi_input)
        self.kaydet_button = QPushButton("Yeni Derslik Ekle")
        self.kaydet_button.clicked.connect(self.kaydet_islemi)
        self.temizle_button = QPushButton("Formu Temizle / İptal")
        self.temizle_button.clicked.connect(self.formu_temizle)
        form_layout.addRow(self.kaydet_button)
        form_layout.addRow(self.temizle_button)

        # --- Sağ Taraf: Arama, Görselleştirme ve Liste ---
        # Sağ tarafın düzenini dikey hale getirdik (önce arama kutusu, sonra tablo)
        right_side_layout = QVBoxLayout()

        # --- ARAMA KUTUSU VE BUTONU (YENİ EKLENDİ) ---
        arama_groupbox = QGroupBox("Arama ve Görselleştirme")
        arama_layout = QHBoxLayout()
        arama_groupbox.setLayout(arama_layout)

        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("Görselleştirmek için Derslik ID'si girin...")
        self.arama_button = QPushButton("Ara ve Görselleştir")
        self.arama_button.clicked.connect(self.arama_yap)

        arama_layout.addWidget(self.arama_input)
        arama_layout.addWidget(self.arama_button)
        # --- ARAMA KISMI SONU ---

        # Derslik tablosu (öncekiyle aynı)
        self.derslik_tablosu = QTableWidget()
        # ... (Tablo ayarları öncekiyle tamamen aynı) ...
        self.derslik_tablosu.setColumnCount(5)
        self.derslik_tablosu.setHorizontalHeaderLabels(["ID", "Derslik Kodu", "Derslik Adı", "Kapasite", "İşlem"])
        self.derslik_tablosu.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.derslik_tablosu.setColumnWidth(4, 100)
        self.derslik_tablosu.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.derslik_tablosu.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.derslik_tablosu.cellClicked.connect(self.formu_doldur)

        # Arama kutusunu ve tabloyu sağ tarafa ekle
        right_side_layout.addWidget(arama_groupbox)
        right_side_layout.addWidget(self.derslik_tablosu)

        # Ana layout'a sol ve sağ tarafları ekle
        main_layout.addWidget(form_container)
        main_layout.addLayout(right_side_layout)

        self.derslikleri_listele()

    # --- YENİ FONKSİYON: ARAMA YAP ---
    def arama_yap(self):
        """Arama kutusundaki ID'ye göre dersliği bulur ve görselleştirir."""
        derslik_id_str = self.arama_input.text().strip()
        if not derslik_id_str.isdigit():
            QMessageBox.warning(self, "Hatalı Giriş", "Lütfen geçerli bir sayısal Derslik ID'si girin.")
            return

        derslik_id = int(derslik_id_str)
        detaylar = database.derslik_detay_getir(derslik_id)

        if detaylar:
            # Derslik bulundu, görselleştirme penceresini oluştur ve göster
            dialog = GorsellestirmeDialog(detaylar, self)
            dialog.exec()  # .exec() pencereyi modal (diğer pencereleri kitleyen) olarak açar
        else:
            QMessageBox.information(self, "Bulunamadı", f"ID: {derslik_id} olan bir derslik bulunamadı.")

    # ... (derslikleri_listele, kaydet_islemi, derslik_ekle, guncelle, sil, formu_doldur, formu_temizle...)
    # ÖNCEKİ KODDAKİ TÜM BU FONKSİYONLAR HİÇBİR DEĞİŞİKLİK OLMADAN AYNI ŞEKİLDE KALACAK.
    # Onları buraya tekrar kopyalamıyorum, sadece yerlerini belirtiyorum.
    def derslikleri_listele(self):
        # ... (öncekiyle aynı kod)
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            self.derslik_tablosu.setRowCount(0)
            return
        derslikler = database.derslikleri_getir(bolum_id)
        self.derslik_tablosu.setRowCount(len(derslikler))
        for row_num, derslik_data in enumerate(derslikler):
            for col_num, data in enumerate(derslik_data):
                self.derslik_tablosu.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            derslik_id = derslik_data[0]
            sil_button = QPushButton("Sil")
            sil_button.clicked.connect(lambda checked, id=derslik_id: self.derslik_sil(id))
            self.derslik_tablosu.setCellWidget(row_num, 4, sil_button)

    def kaydet_islemi(self):
        # ... (öncekiyle aynı kod)
        if self.secili_derslik_id is None:
            self.derslik_ekle()
        else:
            self.derslik_guncelle()

    def derslik_ekle(self):
        # ... (öncekiyle aynı kod)
        derslik_bilgileri = {"bolum_id": self.user_info.get('bolum_id'), "derslik_kodu": self.derslik_kodu_input.text(),
                             "derslik_adi": self.derslik_adi_input.text(), "kapasite": self.kapasite_input.value(),
                             "enine_sira": self.enine_sira_input.value(), "boyuna_sira": self.boyuna_sira_input.value(),
                             "sira_yapisi": self.sira_yapisi_input.currentText()}
        if not derslik_bilgileri["derslik_kodu"] or not derslik_bilgileri["derslik_adi"]: QMessageBox.warning(self,
                                                                                                              "Hata",
                                                                                                              "Derslik Kodu ve Adı boş bırakılamaz."); return
        basarili, mesaj = database.derslik_ekle(derslik_bilgileri)
        if basarili:
            QMessageBox.information(self, "Başarılı", mesaj); self.derslikleri_listele(); self.formu_temizle()
        else:
            QMessageBox.critical(self, "Başarısız", mesaj)

    def derslik_guncelle(self):
        # ... (öncekiyle aynı kod)
        derslik_bilgileri = {"derslik_id": self.secili_derslik_id, "derslik_kodu": self.derslik_kodu_input.text(),
                             "derslik_adi": self.derslik_adi_input.text(), "kapasite": self.kapasite_input.value(),
                             "enine_sira": self.enine_sira_input.value(), "boyuna_sira": self.boyuna_sira_input.value(),
                             "sira_yapisi": self.sira_yapisi_input.currentText()}
        basarili, mesaj = database.derslik_guncelle(derslik_bilgileri)
        if basarili:
            QMessageBox.information(self, "Başarılı", mesaj); self.derslikleri_listele(); self.formu_temizle()
        else:
            QMessageBox.critical(self, "Başarısız", mesaj)

    def derslik_sil(self, derslik_id):
        # ... (öncekiyle aynı kod)
        onay_mesaji = QMessageBox.question(self, "Silme Onayı",
                                           f"ID: {derslik_id} olan dersliği silmek istediğinizden emin misiniz?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if onay_mesaji == QMessageBox.StandardButton.Yes:
            basarili, mesaj = database.derslik_sil(derslik_id)
            if basarili:
                QMessageBox.information(self, "Başarılı", mesaj); self.derslikleri_listele()
            else:
                QMessageBox.critical(self, "Başarısız", mesaj)

    def formu_doldur(self, row, column):
        # ... (öncekiyle aynı kod)
        derslik_id_item = self.derslik_tablosu.item(row, 0)
        if not derslik_id_item: return
        self.secili_derslik_id = int(derslik_id_item.text())
        detaylar = database.derslik_detay_getir(self.secili_derslik_id)
        if detaylar:
            self.derslik_kodu_input.setText(detaylar[2]);
            self.derslik_adi_input.setText(detaylar[3]);
            self.kapasite_input.setValue(detaylar[4]);
            self.enine_sira_input.setValue(detaylar[5]);
            self.boyuna_sira_input.setValue(detaylar[6]);
            self.sira_yapisi_input.setCurrentText(detaylar[7]);
            self.kaydet_button.setText("Dersliği Güncelle")

    def formu_temizle(self):
        # ... (öncekiyle aynı kod)
        self.secili_derslik_id = None;
        self.derslik_kodu_input.clear();
        self.derslik_adi_input.clear();
        self.kapasite_input.setValue(10);
        self.enine_sira_input.setValue(1);
        self.boyuna_sira_input.setValue(1);
        self.sira_yapisi_input.setCurrentIndex(0);
        self.kaydet_button.setText("Yeni Derslik Ekle");
        self.derslik_tablosu.clearSelection()