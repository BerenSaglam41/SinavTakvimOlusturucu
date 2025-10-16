from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor
from database import kullanici_dogrula


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dinamik Sınav Takvimi - Giriş')
        self.resize(480, 420)
        self.setMinimumSize(420, 380)
        self.setStyleSheet(self._qss())

        # === Arkaplan ===
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        # === Kart ===
        self.card = QFrame(objectName="card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(14)

        # Yumuşak gölge (Qt stylesheet box-shadow desteklemez)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(22, 28, 45, 40))  # hafif
        self.card.setGraphicsEffect(shadow)

        # Başlıklar
        title = QLabel("Hoş geldin 👋")
        title.setObjectName("title")
        subtitle = QLabel("Hesabınla giriş yap")
        subtitle.setObjectName("subtitle")

        # E-posta (validator YOK)
        email_label = QLabel("E-posta")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@kocaeli.edu.tr")

        # Şifre (göster/gizle)
        sifre_label = QLabel("Şifre")
        self.sifre_input = QLineEdit()
        self.sifre_input.setPlaceholderText("••••••••")
        self.sifre_input.setEchoMode(QLineEdit.EchoMode.Password)

        toggle_btn = QPushButton("Göster")
        toggle_btn.setObjectName("ghost")
        toggle_btn.setCheckable(True)
        toggle_btn.clicked.connect(self._toggle_password)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(8)
        pw_row.addWidget(self.sifre_input, 1)
        pw_row.addWidget(toggle_btn, 0, Qt.AlignmentFlag.AlignRight)

        # Giriş butonu
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setDefault(True)  # Enter tuşu
        self.login_button.setEnabled(False)

        # Sinyaller
        self.login_button.clicked.connect(self.handle_login)
        self.email_input.textChanged.connect(self._update_button_state)
        self.sifre_input.textChanged.connect(self._update_button_state)

        # Kart layout yerleşimi
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(6)

        card_layout.addWidget(email_label)
        card_layout.addWidget(self.email_input)

        card_layout.addWidget(sifre_label)
        card_layout.addLayout(pw_row)

        card_layout.addSpacing(8)
        card_layout.addWidget(self.login_button)

        # Karta hafif ortalama
        root.addStretch(1)
        root.addWidget(self.card, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(2)

    # ---------- Stil ----------
    def _qss(self) -> str:
        return """
        QWidget {
            background: #F5F7FB;
            font-family: 'Inter', 'Segoe UI', Arial;
            font-size: 15px;
            color: #1F2937;
        }
        #card {
            background: #FFFFFF;
            border-radius: 18px;
            border: 1px solid #EEF2F7;
        }
        #title {
            font-size: 24px;
            font-weight: 700;
            color: #111827;
        }
        #subtitle {
            font-size: 13px;
            color: #6B7280;
            margin-bottom: 8px;
        }
        QLabel {
            font-size: 13px;
            color: #374151;
        }
        QLineEdit {
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            background: #F9FAFB;
        }
        QLineEdit:focus {
            border: 1px solid #93C5FD;
            background: #FFFFFF;
        }
        QPushButton {
            padding: 10px 14px;
            border-radius: 12px;
            background: #3B82F6;
            color: white;
            border: none;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #2563EB;
        }
        QPushButton:disabled {
            background: #BFDBFE;
            color: #F3F4F6;
        }
        QPushButton#ghost {
            background: transparent;
            color: #3B82F6;
            padding: 6px 10px;
            border-radius: 8px;
        }
        QPushButton#ghost:hover {
            background: #EFF6FF;
        }
        """

    # ---------- Yardımcılar ----------
    def _toggle_password(self, checked: bool):
        self.sifre_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        sender = self.sender()
        if isinstance(sender, QPushButton):
            sender.setText("Gizle" if checked else "Göster")

    def _update_button_state(self):
        # Test sürümü: e-posta format kontrolü yok, sadece boş olmama
        email_ok = len(self.email_input.text().strip()) > 0
        pw_ok = len(self.sifre_input.text()) > 0
        self.login_button.setEnabled(email_ok and pw_ok)

    def _normalize_user_info(self, ui) -> dict | None:
        if not ui:
            return None
        if isinstance(ui, dict):
            return {
                "id": ui.get("id"),
                "email": ui.get("email") or ui.get("mail"),
                "rol": ui.get("rol") or ui.get("role") or ui.get("yetki"),
                "bolum_id": ui.get("bolum_id") or ui.get("department_id"),
            }
        if isinstance(ui, (tuple, list)):
            _get = lambda i: ui[i] if i < len(ui) else None
            return {
                "id": _get(0),
                "email": _get(1),
                "rol": _get(2),
                "bolum_id": _get(3),
            }
        return None

    def _shake_card(self):
        anim = QPropertyAnimation(self.card, b"pos", self)
        start = self.card.pos()
        anim.setDuration(220)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        dx = 12
        key_values = [
            (0.0, start),
            (0.20, start + QPoint(dx, 0)),
            (0.40, start - QPoint(dx, 0)),
            (0.60, start + QPoint(dx // 2, 0)),
            (0.80, start - QPoint(dx // 2, 0)),
            (1.0, start),
        ]
        for k, v in key_values:
            anim.setKeyValueAt(k, v)
        anim.start()

    # ---------- Giriş ----------
    def handle_login(self):
        email = self.email_input.text().strip()
        sifre = self.sifre_input.text()

        # Test sürümü: sadece boş alan uyarısı
        if not email or not sifre:
            QMessageBox.warning(self, "Eksik Bilgi", "E-posta ve şifre alanları boş bırakılamaz.")
            return

        try:
            raw = kullanici_dogrula(email, sifre)
        except Exception as e:
            QMessageBox.critical(self, "Bağlantı Hatası", f"Veritabanı hatası:\n{e}")
            self._shake_card()
            return

        user_data = self._normalize_user_info(raw)
        if not user_data or not user_data.get("id"):
            QMessageBox.critical(self, "Giriş Başarısız", "E-posta veya şifre hatalı!")
            self._shake_card()
            return

        self.login_success.emit(user_data)
        self.close()
