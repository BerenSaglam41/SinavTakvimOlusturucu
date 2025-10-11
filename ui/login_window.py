# Gerekli PyQt6 modüllerini ve database fonksiyonunu içe aktaralım
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from database import kullanici_dogrula
from PyQt6.QtCore import pyqtSignal

class LoginWindow(QWidget):
    # Giriş başarılı olduğunda kullanıcı bilgilerini içeren bir sinyal tanımla
    login_success = pyqtSignal(dict)
    def __init__(self):
        super().__init__()

        # --- Pencere Ayarları ---
        self.setWindowTitle('Dinamik Sınav Takvimi - Kullanıcı Girişi')
        self.setFixedSize(350, 200)  # Pencerenin boyutunu sabitle

        # --- Arayüz Elemanları (Widget'lar) ---
        self.email_label = QLabel('E-posta Adresi:')
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('ornek@kocaeli.edu.tr')

        self.sifre_label = QLabel('Şifre:')
        self.sifre_input = QLineEdit()
        self.sifre_input.setEchoMode(QLineEdit.EchoMode.Password) # Şifreyi gizle

        self.login_button = QPushButton('Giriş Yap')

        # --- Tasarım (Layout) ---
        # Widget'ları dikey bir kutu düzenine yerleştirelim
        layout = QVBoxLayout()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.sifre_label)
        layout.addWidget(self.sifre_input)
        layout.addStretch() # Buton ile input arasına boşluk koyar
        layout.addWidget(self.login_button)

        self.setLayout(layout) # Oluşturduğumuz düzeni pencereye uygula

        # --- Sinyal ve Slot Bağlantısı ---
        # "Giriş Yap" butonuna tıklandığında hangi fonksiyonun çalışacağını belirtelim
        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        """'Giriş Yap' butonuna basıldığında çalışan fonksiyon."""
        email = self.email_input.text()
        sifre = self.sifre_input.text()

        if not email or not sifre:
            QMessageBox.warning(self, 'Hata', 'E-posta ve şifre alanları boş bırakılamaz!')
            return

        # Veritabanından kullanıcıyı doğrula
        user_info = kullanici_dogrula(email, sifre)
        if user_info:
            # Kullanıcı bilgilerini bir sözlük olarak hazırlayalım
            user_data = {
                'id': user_info[0],
                'email': user_info[1],
                'rol': user_info[2],
                'bolum_id': user_info[3]
            }
            # Başarı sinyalini yay ve pencereyi kapat
            self.login_success.emit(user_data)
            self.close()
        else:
            QMessageBox.critical(self, 'Giriş Başarısız', 'E-posta veya şifre hatalı!')
