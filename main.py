import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class AppController:
    def __init__(self):
        self.login_win = None
        self.main_win = None

    def show_login(self):
        self.login_win = LoginWindow()
        # Login penceresinin başarı sinyalini, ana pencereyi açacak fonksiyona bağla
        self.login_win.login_success.connect(self.show_main_window)
        self.login_win.show()

    def show_main_window(self, user_info):
        # Login başarılı olunca bu fonksiyon çalışır
        self.main_win = MainWindow(user_info)
        self.main_win.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = AppController()
    controller.show_login() # Uygulamayı giriş ekranını göstererek başlat
    sys.exit(app.exec())