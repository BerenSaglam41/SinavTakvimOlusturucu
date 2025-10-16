from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QFrame, QHBoxLayout, QWidget, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class GorsellestirmeDialog(QDialog):
    def __init__(self, derslik_detaylari, parent=None):
        super().__init__(parent)

        derslik_adi = derslik_detaylari[3]
        enine_sira = derslik_detaylari[5]
        boyuna_sira = derslik_detaylari[6]
        sira_yapisi = derslik_detaylari[7]

        # Ana pencere stilini belirle (Glassmorphism + açık premium arka plan)
        self.setStyleSheet("""
            QDialog {
                background: #F5F5F7;
                font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                font-size: 18px;
                color: #1A202C;
            }
        """)
        self.setWindowTitle(f"Oturma Düzeni: {derslik_adi} ({sira_yapisi})")

        main_layout = QGridLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)

        for satir in range(boyuna_sira):
            for sutun in range(enine_sira):
                desk_group_frame = QFrame()
                desk_group_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

                # Glassmorphism efekti style
                desk_group_frame.setStyleSheet("""
                    background: rgba(255, 255, 255, 0.45);
                    border: 2px solid rgba(0, 122, 255, 0.25);
                    border-radius: 18px;
                    box-shadow: 0px 4px 24px 0px rgba(30, 42, 60, 0.09);
                """)

                desk_layout = QHBoxLayout(desk_group_frame)
                desk_layout.setContentsMargins(14, 8, 14, 8)
                desk_layout.setSpacing(12)

                def seat_style(accent):
                    return f"""
                        background: {accent};
                        border-radius: 8px;
                        min-width: 26px;
                        min-height: 32px;
                        border: 1.5px solid #F0F2FA;
                        box-shadow: 0 2px 8px 0 rgba(0,0,0,0.05);
                    """

                if sira_yapisi == "İkişerli":
                    seat1 = QWidget()
                    seat1.setStyleSheet(seat_style("#007AFF"))
                    divider = QFrame()
                    divider.setFixedWidth(7)
                    divider.setFrameShape(QFrame.Shape.VLine)
                    divider.setFrameShadow(QFrame.Shadow.Plain)
                    seat2 = QWidget()
                    seat2.setStyleSheet(seat_style("#007AFF"))
                    desk_layout.addWidget(seat1)
                    desk_layout.addWidget(divider)
                    desk_layout.addWidget(seat2)
                    desk_group_frame.setFixedSize(112, 48)

                elif sira_yapisi == "Üçerli":
                    seat1 = QWidget()
                    seat1.setStyleSheet(seat_style("#31C48D"))  # premium yeşil vurgusu
                    divider1 = QFrame()
                    divider1.setFixedWidth(7)
                    divider1.setFrameShape(QFrame.Shape.VLine)
                    divider1.setFrameShadow(QFrame.Shadow.Plain)
                    seat2 = QWidget()
                    seat2.setStyleSheet(seat_style("#31C48D"))
                    divider2 = QFrame()
                    divider2.setFixedWidth(7)
                    divider2.setFrameShape(QFrame.Shape.VLine)
                    divider2.setFrameShadow(QFrame.Shadow.Plain)
                    seat3 = QWidget()
                    seat3.setStyleSheet(seat_style("#31C48D"))
                    desk_layout.addWidget(seat1)
                    desk_layout.addWidget(divider1)
                    desk_layout.addWidget(seat2)
                    desk_layout.addWidget(divider2)
                    desk_layout.addWidget(seat3)
                    desk_group_frame.setFixedSize(172, 48)

                elif sira_yapisi == "Dorderli":
                    seat1 = QWidget()
                    seat1.setStyleSheet(seat_style("#FF7F50"))  # Akçora mercan
                    divider1 = QFrame()
                    divider1.setFixedWidth(7)
                    divider1.setFrameShape(QFrame.Shape.VLine)
                    divider1.setFrameShadow(QFrame.Shadow.Plain)
                    seat2 = QWidget()
                    seat2.setStyleSheet(seat_style("#FF7F50"))
                    divider2 = QFrame()
                    divider2.setFixedWidth(7)
                    divider2.setFrameShape(QFrame.Shape.VLine)
                    divider2.setFrameShadow(QFrame.Shadow.Plain)
                    seat3 = QWidget()
                    seat3.setStyleSheet(seat_style("#FF7F50"))
                    divider3 = QFrame()
                    divider3.setFixedWidth(7)
                    divider3.setFrameShape(QFrame.Shape.VLine)
                    divider3.setFrameShadow(QFrame.Shadow.Plain)
                    seat4 = QWidget()
                    seat4.setStyleSheet(seat_style("#FF7F50"))
                    desk_layout.addWidget(seat1)
                    desk_layout.addWidget(divider1)
                    desk_layout.addWidget(seat2)
                    desk_layout.addWidget(divider2)
                    desk_layout.addWidget(seat3)
                    desk_layout.addWidget(divider3)
                    desk_layout.addWidget(seat4)
                    desk_group_frame.setFixedSize(230, 48)

                else:  # Tekli veya diğer
                    seat1 = QWidget()
                    seat1.setStyleSheet(seat_style("#3245FF"))  # Farklı mavi vurgusu
                    desk_layout.addWidget(seat1)
                    desk_group_frame.setFixedSize(64, 48)

                main_layout.addWidget(desk_group_frame, satir, sutun, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)
