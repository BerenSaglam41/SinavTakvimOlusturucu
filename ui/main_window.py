from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from PyQt6.QtCore import Qt
import database
from ui.view_derslik import DerslikView
from ui.view_veri_yukleme import VeriYuklemeView
from ui.view_kayit_goruntuleme import KayitGoruntulemeView
from ui.view_sinav_olusturma import SinavOlusturmaView


class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()

        self.user_info = user_info

        # --- Pencere Ayarları ---
        self.setWindowTitle('Dinamik Sınav Takvimi Yönetim Paneli')
        self.setGeometry(100, 100, 1200, 700)

        # --- Durum Değişkenleri ---
        self.dersler_yuklendi = False
        self.ogrenciler_yuklendi = False

        # --- Ana Arayüz ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Sol Navigasyon Menüsü ---
        self.nav_menu = QListWidget()
        self.nav_menu.setFixedWidth(200)
        main_layout.addWidget(self.nav_menu)

        # --- Sağ İçerik Alanı (Değişen Sayfalar) ---
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # --- Kurulum ---
        self.create_views_and_menu()
        self.nav_menu.currentItemChanged.connect(self.change_view)

        self.initial_data_check()

    def create_views_and_menu(self):
        """Menü elemanlarını ve karşılık gelen sayfaları oluşturur."""
        self.derslik_view = DerslikView(self.user_info)
        self.stacked_widget.addWidget(self.derslik_view)
        self.nav_menu.addItem("Derslik İşlemleri")

        self.veri_yukleme_view = VeriYuklemeView(self.user_info)
        self.stacked_widget.addWidget(self.veri_yukleme_view)
        self.nav_menu.addItem("Veri Yükleme")
        self.veri_yukleme_view.veri_yuklendi_sinyali.connect(self.on_veri_yuklendi)

        self.kayit_goruntuleme_view = KayitGoruntulemeView(self.user_info)
        self.stacked_widget.addWidget(self.kayit_goruntuleme_view)
        kayit_item = QListWidgetItem("Kayıt Görüntüleme")
        self.nav_menu.addItem(kayit_item)
        kayit_item.setFlags(kayit_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)

        self.sinav_olusturma_view = SinavOlusturmaView(self.user_info)
        self.stacked_widget.addWidget(self.sinav_olusturma_view)
        sinav_item = QListWidgetItem("Sınav Programı Oluştur")
        self.nav_menu.addItem(sinav_item)
        sinav_item.setFlags(sinav_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)

    def change_view(self, item):
        """Menüden bir eleman seçildiğinde ilgili sayfayı gösterir."""
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

    def on_veri_yuklendi(self, veri_tipi):
        """VeriYuklemeView'dan gelen sinyali yakalar ve durumu günceller."""
        if veri_tipi == 'ders':
            self.dersler_yuklendi = True
        elif veri_tipi == 'ogrenci':
            self.ogrenciler_yuklendi = True

        self.update_menu_status()

    def update_menu_status(self):
        """Durum değişkenlerine göre menülerin aktif/pasif durumunu günceller."""
        if self.dersler_yuklendi and self.ogrenciler_yuklendi:
            for i in range(self.nav_menu.count()):
                item = self.nav_menu.item(i)
                text = item.text()
                if text == "Kayıt Görüntüleme" or text == "Sınav Programı Oluştur":
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)

            print("Kayıt Görüntüleme ve Sınav Programı Oluşturma menüleri aktifleştirildi.")

    def initial_data_check(self):
        """Uygulama açıldığında veritabanını kontrol ederek menülerin durumunu ayarlar."""
        bolum_id = self.user_info.get('bolum_id')
        if not bolum_id:
            return

        print("Başlangıç veri kontrolü yapılıyor...")
        if database.ders_verisi_var_mi(bolum_id):
            self.dersler_yuklendi = True
            print(" -> Mevcut ders verisi bulundu.")

        if database.ogrenci_verisi_var_mi(bolum_id):
            self.ogrenciler_yuklendi = True
            print(" -> Mevcut öğrenci verisi bulundu.")

        self.update_menu_status()