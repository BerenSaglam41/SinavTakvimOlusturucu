from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
import database
from ui.view_derslik import DerslikView
from ui.view_veri_yukleme import VeriYuklemeView
from ui.view_kayit_goruntuleme import KayitGoruntulemeView
from ui.view_sinav_olusturma import SinavOlusturmaView
from ui.view_oturma_plani import OturmaPlaniView

class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.setWindowTitle('Dinamik Sınav Takvimi Yönetim Paneli')
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #F5F5F7;
                font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                font-size: 15px;
                color: #222c37;
            }
        """)

        # LOGO
        logo_yolu = os.path.join(os.path.dirname(__file__), "..", "logo.png")
        logo_label = QLabel()
        pixmap = QPixmap(logo_yolu)
        pixmap = pixmap.scaledToHeight(62, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ana layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(logo_label)  # LOGO EN ÜSTTE

        # Alt tarafta navigasyon ve içerik
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Sol Navigasyon
        self.nav_menu = QListWidget()
        self.nav_menu.setFixedWidth(220)
        self.nav_menu.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007AFF, stop:1 #3A86FF);
                color: #fff;
                border: none;
                font-size: 16px;
                font-weight: 600;
                padding: 16px 0;
            }
            QListWidget::item {
                border-radius: 7px;
                margin: 5px 18px 5px 18px;
                padding: 10px 6px;
                background: transparent;
            }
            QListWidget::item:selected {
                background: rgba(255,255,255,0.20);
                color: #fff;
            }
            QListWidget::item:disabled {
                color: #a6b1bc;
                background: transparent;
            }
        """)
        content_layout.addWidget(self.nav_menu)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background: transparent;
                border-radius: 18px;
            }
        """)
        content_layout.addWidget(self.stacked_widget)

        # Kurulum - (Diğer kodlar aynen)
        self.dersler_yuklendi = False
        self.ogrenciler_yuklendi = False
        self.program_olusturuldu = False

        self.create_views_and_menu()
        self.nav_menu.currentItemChanged.connect(self.change_view)
        self.initial_data_check()

    def create_views_and_menu(self):
        # 1. Derslik Sayfası
        self.derslik_view = DerslikView(self.user_info)
        self.stacked_widget.addWidget(self.derslik_view)
        derslik_item = QListWidgetItem("Derslik İşlemleri")
        self.nav_menu.addItem(derslik_item)

        # 2. Veri Yükleme Sayfası
        self.veri_yukleme_view = VeriYuklemeView(self.user_info)
        self.stacked_widget.addWidget(self.veri_yukleme_view)
        veri_item = QListWidgetItem("Veri Yükleme")
        self.nav_menu.addItem(veri_item)
        self.veri_yukleme_view.veri_yuklendi_sinyali.connect(self.on_veri_yuklendi)

        # 3. Kayıt Görüntüleme Sayfası
        self.kayit_goruntuleme_view = KayitGoruntulemeView(self.user_info)
        self.stacked_widget.addWidget(self.kayit_goruntuleme_view)
        kayit_item = QListWidgetItem("Kayıt Görüntüleme")
        kayit_item.setFlags(kayit_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.nav_menu.addItem(kayit_item)

        # 4. Sınav Oluşturma Sayfası
        self.sinav_olusturma_view = SinavOlusturmaView(self.user_info)
        self.sinav_olusturma_view.program_basariyla_olusturuldu.connect(self.on_program_olusturuldu)
        self.stacked_widget.addWidget(self.sinav_olusturma_view)
        sinav_item = QListWidgetItem("Sınav Programı Oluştur")
        sinav_item.setFlags(sinav_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.nav_menu.addItem(sinav_item)

        # 5. Oturma Planı Sayfası
        self.oturma_plani_view = OturmaPlaniView(self.user_info)
        self.stacked_widget.addWidget(self.oturma_plani_view)
        oturma_plani_item = QListWidgetItem("Oturma Planı Oluştur")
        oturma_plani_item.setFlags(oturma_plani_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.nav_menu.addItem(oturma_plani_item)

    def change_view(self, item):
        if not item:
            return
        text = item.text()
        if text == "Derslik İşlemleri":
            self.stacked_widget.setCurrentWidget(self.derslik_view)
        elif text == "Veri Yükleme":
            self.stacked_widget.setCurrentWidget(self.veri_yukleme_view)
        elif text == "Kayıt Görüntüleme":
            self.kayit_goruntuleme_view.load_data()
            self.stacked_widget.setCurrentWidget(self.kayit_goruntuleme_view)
        elif text == "Sınav Programı Oluştur":
            self.sinav_olusturma_view.load_data()
            self.stacked_widget.setCurrentWidget(self.sinav_olusturma_view)
        elif text == "Oturma Planı Oluştur":
            self.oturma_plani_view.load_data()
            self.stacked_widget.setCurrentWidget(self.oturma_plani_view)

    def on_veri_yuklendi(self, veri_tipi):
        if veri_tipi == 'ders':
            self.dersler_yuklendi = True
        elif veri_tipi == 'ogrenci':
            self.ogrenciler_yuklendi = True
        self.update_menu_status()

    def on_program_olusturuldu(self):
        self.program_olusturuldu = True
        self.update_menu_status()

    def update_menu_status(self):
        if self.dersler_yuklendi and self.ogrenciler_yuklendi:
            for i in range(self.nav_menu.count()):
                item = self.nav_menu.item(i)
                text = item.text()
                if text == "Kayıt Görüntüleme" or text == "Sınav Programı Oluştur":
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        if self.program_olusturuldu:
            for i in range(self.nav_menu.count()):
                item = self.nav_menu.item(i)
                if item.text() == "Oturma Planı Oluştur":
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)

    def initial_data_check(self):
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            return
        if database.ders_verisi_var_mi(bolum_id):
            self.dersler_yuklendi = True
        if database.ogrenci_verisi_var_mi(bolum_id):
            self.ogrenciler_yuklendi = True
        if database.sinav_programi_var_mi(bolum_id):
            self.program_olusturuldu = True
        self.update_menu_status()
