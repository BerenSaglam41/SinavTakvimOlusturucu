from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFormLayout, QSpinBox, QComboBox, QMessageBox)
import database  # database.py dosyasındaki fonksiyonları kullanmak için


class DerslikView(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info  # Giriş yapan kullanıcının bilgilerini sakla

        # Ana layout (yatay)
        main_layout = QHBoxLayout(self)

        # --- Sol Taraf: Giriş Formu ---
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_container.setFixedWidth(350)

        self.derslik_kodu_input = QLineEdit()
        self.derslik_adi_input = QLineEdit()
        self.kapasite_input = QSpinBox()
        self.kapasite_input.setRange(10, 200)  # Minimum ve maksimum kapasite
        self.enine_sira_input = QSpinBox()
        self.enine_sira_input.setRange(1, 20)
        self.boyuna_sira_input = QSpinBox()
        self.boyuna_sira_input.setRange(1, 20)
        self.sira_yapisi_input = QComboBox()
        self.sira_yapisi_input.addItems(["İkişerli", "Üçerli", "Tekli"])

        form_layout.addRow("Derslik Kodu:", self.derslik_kodu_input)
        form_layout.addRow("Derslik Adı:", self.derslik_adi_input)
        form_layout.addRow("Kapasite:", self.kapasite_input)
        form_layout.addRow("Enine Sıra Sayısı (Sütun):", self.enine_sira_input)
        form_layout.addRow("Boyuna Sıra Sayısı (Satır):", self.boyuna_sira_input)
        form_layout.addRow("Sıra Yapısı:", self.sira_yapisi_input)

        self.ekle_button = QPushButton("Yeni Derslik Ekle")
        self.ekle_button.clicked.connect(self.derslik_ekle)
        form_layout.addRow(self.ekle_button)

        # --- Sağ Taraf: Derslik Listesi Tablosu ---
        self.derslik_tablosu = QTableWidget()
        self.derslik_tablosu.setColumnCount(5)
        self.derslik_tablosu.setHorizontalHeaderLabels(["ID", "Derslik Kodu", "Derslik Adı", "Kapasite", "Islem"])
        self.derslik_tablosu.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.derslik_tablosu.setColumnWidth(4, 100) # Silme butonu sütununu sabitle
        self.derslik_tablosu.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        self.derslik_tablosu.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Tabloyu düzenlenemez yap

        main_layout.addWidget(form_container)
        main_layout.addWidget(self.derslik_tablosu)

        # Sayfa ilk açıldığında derslikleri listele
        self.derslikleri_listele()

    def derslikleri_listele(self):
        """Veritabanından derslikleri çeker ve tabloyu en güncel haliyle doldurur."""
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            self.derslik_tablosu.setRowCount(0)
            return

        derslikler = database.derslikleri_getir(bolum_id)

        self.derslik_tablosu.setRowCount(len(derslikler))

        # Her bir derslik için tabloya yeni bir satır ekle
        for row_num, derslik_data in enumerate(derslikler):
            # derslik_data = (derslik_id, derslik_kodu, derslik_adi, kapasite)

            # İlk 4 sütunu (ID, Kod, Ad, Kapasite) verilerle doldur
            for col_num, data in enumerate(derslik_data):
                self.derslik_tablosu.setItem(row_num, col_num, QTableWidgetItem(str(data)))

            # 5. Sütuna özel olarak "Sil" butonunu oluştur ve ekle
            derslik_id = derslik_data[0]  # O anki satırın ID'sini al (ilk sütun)
            sil_button = QPushButton("Sil")

            # Butonun `clicked` sinyalini, `derslik_sil` fonksiyonuna bağla.
            # `lambda` kullanarak o anki `derslik_id`'nin silme fonksiyonuna
            # parametre olarak gönderilmesini sağlıyoruz.
            sil_button.clicked.connect(lambda checked, id=derslik_id: self.derslik_sil(id))

            # Oluşturulan butonu 5. sütuna (indeksi 4) yerleştir
            self.derslik_tablosu.setCellWidget(row_num, 4, sil_button)

    def derslik_ekle(self):
        """Formdaki bilgileri alıp veritabanına yeni derslik ekler."""
        derslik_bilgileri = {
            "bolum_id": self.user_info.get('bolum_id'),
            "derslik_kodu": self.derslik_kodu_input.text(),
            "derslik_adi": self.derslik_adi_input.text(),
            "kapasite": self.kapasite_input.value(),
            "enine_sira": self.enine_sira_input.value(),
            "boyuna_sira": self.boyuna_sira_input.value(),
            "sira_yapisi": self.sira_yapisi_input.currentText()
        }

        # Basit bir kontrol
        if not derslik_bilgileri["derslik_kodu"] or not derslik_bilgileri["derslik_adi"]:
            QMessageBox.warning(self, "Hata", "Derslik Kodu ve Adı boş bırakılamaz.")
            return

        basarili, mesaj = database.derslik_ekle(derslik_bilgileri)

        if basarili:
            QMessageBox.information(self, "Başarılı", mesaj)
            self.derslikleri_listele()  # Tabloyu yenile
            # Formu temizle
            self.derslik_kodu_input.clear()
            self.derslik_adi_input.clear()
        else:
            QMessageBox.critical(self, "Başarısız", mesaj)

    def derslik_sil(self, derslik_id):
        """Kullanıcıya onay sorduktan sonra dersliği siler."""

        # Emin misiniz diye sor
        onay_mesaji = QMessageBox.question(self,
                                           "Silme Onayı",
                                           f"ID: {derslik_id} olan dersliği silmek istediğinizden emin misiniz?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if onay_mesaji == QMessageBox.StandardButton.Yes:
            # Kullanıcı "Evet" derse silme işlemini yap
            basarili, mesaj = database.derslik_sil(derslik_id)

            if basarili:
                QMessageBox.information(self, "Başarılı", mesaj)
                self.derslikleri_listele()  # Tabloyu yenile
            else:
                QMessageBox.critical(self, "Başarısız", mesaj)