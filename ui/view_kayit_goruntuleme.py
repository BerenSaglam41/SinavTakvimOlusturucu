from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QListWidget, QMessageBox, QTabWidget)
import database


class KayitGoruntulemeView(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.bolum_dersleri = []  # Bölüm derslerini hafızada tutmak için

        # Ana layout ve Sekmeli Widget
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Sekme 1: Öğrenci Arama
        self.ogrenci_arama_tab = QWidget()
        self.setup_ogrenci_arama_ui()
        self.tabs.addTab(self.ogrenci_arama_tab, "Öğrenciye Göre Arama")

        # Sekme 2: Ders Listesi
        self.ders_listesi_tab = QWidget()
        self.setup_ders_listesi_ui()
        self.tabs.addTab(self.ders_listesi_tab, "Derse Göre Listeleme")

    def setup_ogrenci_arama_ui(self):
        layout = QVBoxLayout(self.ogrenci_arama_tab)

        arama_layout = QHBoxLayout()
        self.ogrenci_no_input = QLineEdit()
        self.ogrenci_no_input.setPlaceholderText("Öğrenci Numarası Girin...")
        self.arama_button = QPushButton("Ara")
        arama_layout.addWidget(self.ogrenci_no_input)
        arama_layout.addWidget(self.arama_button)

        self.ogrenci_adi_label = QLabel("Aranan Öğrenci: -")
        self.aldigi_dersler_list = QListWidget()

        layout.addLayout(arama_layout)
        layout.addWidget(self.ogrenci_adi_label)
        layout.addWidget(QLabel("Aldığı Dersler:"))
        layout.addWidget(self.aldigi_dersler_list)

        self.arama_button.clicked.connect(self.ogrenci_ara)

    def setup_ders_listesi_ui(self):
        layout = QHBoxLayout(self.ders_listesi_tab)

        sol_taraf = QVBoxLayout()
        self.dersler_listesi_widget = QListWidget()
        sol_taraf.addWidget(QLabel("Bölümdeki Tüm Dersler:"))
        sol_taraf.addWidget(self.dersler_listesi_widget)

        sag_taraf = QVBoxLayout()
        self.dersi_alanlar_list = QListWidget()
        sag_taraf.addWidget(QLabel("Dersi Alan Öğrenciler:"))
        sag_taraf.addWidget(self.dersi_alanlar_list)

        layout.addLayout(sol_taraf, 1)  # 1 oranında yer kapla
        layout.addLayout(sag_taraf, 2)  # 2 oranında yer kapla

        self.dersler_listesi_widget.currentItemChanged.connect(self.ders_secildi)

    def load_data(self):
        """Bu sayfa görünür olduğunda çağrılacak fonksiyon."""
        self.bolum_dersleri = database.bolumun_derslerini_getir(self.user_info.get('bolum_id'))
        self.dersler_listesi_widget.clear()
        for ders_id, ders_kodu, ders_adi in self.bolum_dersleri:
            # Her bir elemana görünmez bir şekilde ders_id'yi de saklayalım
            item_text = f"{ders_kodu} - {ders_adi}"
            self.dersler_listesi_widget.addItem(item_text)
            self.dersler_listesi_widget.item(self.dersler_listesi_widget.count() - 1).setData(32,
                                                                                              ders_id)  # 32: UserRole

    def ogrenci_ara(self):
        ogrenci_no = self.ogrenci_no_input.text().strip()
        if not ogrenci_no:
            return

        ogrenci_adi, dersler = database.ogrenci_derslerini_getir(ogrenci_no, self.user_info.get('bolum_id'))

        if ogrenci_adi:
            self.ogrenci_adi_label.setText(f"Aranan Öğrenci: {ogrenci_adi}")
            self.aldigi_dersler_list.clear()
            self.aldigi_dersler_list.addItems(dersler)
        else:
            QMessageBox.information(self, "Bulunamadı",
                                    f"'{ogrenci_no}' numaralı öğrenci bulunamadı veya hiç ders almıyor.")
            self.ogrenci_adi_label.setText("Aranan Öğrenci: -")
            self.aldigi_dersler_list.clear()

    def ders_secildi(self, current_item, previous_item):
        if not current_item:
            return

        ders_id = current_item.data(32)  # Sakladığımız ders_id'yi geri al
        ogrenciler = database.dersi_alan_ogrencileri_getir(ders_id)

        self.dersi_alanlar_list.clear()
        if ogrenciler:
            ogrenci_listesi = [f"{no} - {ad}" for no, ad in ogrenciler]
            self.dersi_alanlar_list.addItems(ogrenci_listesi)