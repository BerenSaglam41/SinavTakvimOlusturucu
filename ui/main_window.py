from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from PyQt6.QtCore import Qt

# Diğer sayfalarımızı (view) import edeceğiz. Şimdilik sadece derslik sayfasını oluşturalım.
# Henüz bu dosyayı oluşturmadık, bir sonraki adımda oluşturacağız.
from ui.view_derslik import DerslikView
from ui.view_veri_yukleme import VeriYuklemeView


class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()

        self.user_info = user_info  # Giriş yapan kullanıcının bilgilerini sakla

        # --- Pencere Ayarları ---
        self.setWindowTitle('Dinamik Sınav Takvimi Yönetim Paneli')
        self.setGeometry(100, 100, 1200, 700)  # Pencere boyutu ve konumu

        # --- Durum Değişkenleri ---
        # Projenin mantığını kontrol etmek için bu değişkenleri kullanacağız.
        self.derslikler_girildi = False
        self.veriler_yuklendi = False  # Ders ve Öğrenci listesi

        # --- Ana Arayüz ---
        # Ana widget ve yatay layout oluştur
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Sol Navigasyon Menüsü ---
        self.nav_menu = QListWidget()
        self.nav_menu.setFixedWidth(200)
        main_layout.addWidget(self.nav_menu)

        # --- Sağ İçerik Alanı (Değişen Sayfalar) ---
        # QStackedWidget, sayfalar arasında geçiş yapmamızı sağlar.
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # --- Sayfaları ve Menüleri Oluştur ---
        self.create_views_and_menu()

        # --- Menüdeki tıklamaları sayfa değişimine bağla ---
        self.nav_menu.currentItemChanged.connect(self.change_view)

    def create_views_and_menu(self):
        """Menü elemanlarını ve karşılık gelen sayfaları oluşturur."""
        # Derslik sayfasını oluştur ve StackedWidget'a ekle
        self.derslik_view = DerslikView(self.user_info)
        self.stacked_widget.addWidget(self.derslik_view)
        self.nav_menu.addItem('Derslik Islemleri')

        # YENİ EKLENEN KISIM: Veri Yükleme sayfası
        self.veri_yukleme_view = VeriYuklemeView(self.user_info)
        self.stacked_widget.addWidget(self.veri_yukleme_view)
        veri_yukleme_item = QListWidgetItem("Veri Yükleme")
        self.nav_menu.addItem(veri_yukleme_item)
        self.veri_yukleme_view.veri_yuklendi_sinyali.connect(self.on_veri_yuklendi)

        # Menüye "Derslik İşlemleri" elemanını ekle
        derslik_item = QListWidgetItem("Derslik İşlemleri")
        self.nav_menu.addItem(derslik_item)

        # --- Diğer sayfalar ve menüler buraya eklenecek ---
        # Örnek:
        # self.ders_ogrenci_view = DersOgrenciView()
        # self.stacked_widget.addWidget(self.ders_ogrenci_view)
        # ders_ogrenci_item = QListWidgetItem("Ders/Öğrenci Listeleri")
        # self.nav_menu.addItem(ders_ogrenci_item)
        # ders_ogrenci_item.setFlags(ders_ogrenci_item.flags() & ~Qt.ItemFlag.ItemIsEnabled) # Başlangıçta pasif yap

    def change_view(self, item):
        """Menüden bir eleman seçildiğinde ilgili sayfayı gösterir."""
        if item.text() == "Derslik İşlemleri":
            self.stacked_widget.setCurrentWidget(self.derslik_view)
        elif item.text() == "Veri Yükleme":
            self.stacked_widget.setCurrentWidget(self.veri_yukleme_view)

    def on_veri_yuklendi(self, veri_tipi):
        """VeriYuklemeView'dan gelen sinyali yakalar ve durumu günceller."""
        if veri_tipi == 'ders':
            self.dersler_yuklendi = True # Durum değişkenini güncelle
            print("Ders listesi başarıyla yüklendi ve durum güncellendi.")
        # elif veri_tipi == 'ogrenci':
        #     self.ogrenciler_yuklendi = True

        # self.update_menu_status() # Menülerin aktif/pasif durumunu kontrol et

    def update_menu_status(self):
        """Durum değişkenlerine göre menülerin aktif/pasif durumunu günceller."""
        # Bu fonksiyonu, derslikler girildiğinde veya Excel yüklendiğinde çağıracağız.
        # Örnek:
        # if self.derslikler_girildi:
        #     self.nav_menu.item(1).setFlags(self.nav_menu.item(1).flags() | Qt.ItemFlag.ItemIsEnabled) # Aktif yap
        pass