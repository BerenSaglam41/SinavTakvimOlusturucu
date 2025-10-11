from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QFrame, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt


class GorsellestirmeDialog(QDialog):
    def __init__(self, derslik_detaylari, parent=None):
        super().__init__(parent)

        derslik_adi = derslik_detaylari[3]
        enine_sira = derslik_detaylari[5]
        boyuna_sira = derslik_detaylari[6]
        sira_yapisi = derslik_detaylari[7]

        self.setWindowTitle(f"Oturma Düzeni: {derslik_adi} ({sira_yapisi})")

        main_layout = QGridLayout(self)
        main_layout.setSpacing(15)

        for satir in range(boyuna_sira):
            for sutun in range(enine_sira):
                desk_group_frame = QFrame()
                desk_group_frame.setFrameShape(QFrame.Shape.StyledPanel)
                desk_group_frame.setStyleSheet(
                    "background-color: #f0f0f0; border: 1px solid #cccccc; border-radius: 5px;")

                desk_layout = QHBoxLayout(desk_group_frame)
                desk_layout.setContentsMargins(5, 5, 5, 5)
                desk_layout.setSpacing(5)

                if sira_yapisi == "İkişerli":
                    seat1 = QWidget();
                    seat1.setStyleSheet("background-color: lightblue; border-radius: 3px;")
                    divider = QFrame();
                    divider.setFrameShape(QFrame.Shape.VLine);
                    divider.setFrameShadow(QFrame.Shadow.Sunken)
                    seat2 = QWidget();
                    seat2.setStyleSheet("background-color: lightblue; border-radius: 3px;")

                    desk_layout.addWidget(seat1)
                    desk_layout.addWidget(divider)
                    desk_layout.addWidget(seat2)
                    desk_group_frame.setFixedSize(100, 40)

                elif sira_yapisi == "Üçerli":
                    seat1 = QWidget();
                    seat1.setStyleSheet("background-color: lightgreen; border-radius: 3px;")
                    divider1 = QFrame();
                    divider1.setFrameShape(QFrame.Shape.VLine);
                    divider1.setFrameShadow(QFrame.Shadow.Sunken)
                    seat2 = QWidget();
                    seat2.setStyleSheet("background-color: lightgreen; border-radius: 3px;")
                    divider2 = QFrame();
                    divider2.setFrameShape(QFrame.Shape.VLine);
                    divider2.setFrameShadow(QFrame.Shadow.Sunken)
                    seat3 = QWidget();
                    seat3.setStyleSheet("background-color: lightgreen; border-radius: 3px;")

                    desk_layout.addWidget(seat1);
                    desk_layout.addWidget(divider1);
                    desk_layout.addWidget(seat2);
                    desk_layout.addWidget(divider2);
                    desk_layout.addWidget(seat3)
                    desk_group_frame.setFixedSize(150, 40)

                # --- DÜZELTİLEN VE DOĞRU BLOK: "4lü" DURUMU ---
                elif sira_yapisi == "4lü":
                    # 4 koltuk ve 3 ayırıcı tanımla
                    seat1 = QWidget();
                    seat1.setStyleSheet("background-color: lightyellow; border-radius: 3px;")
                    divider1 = QFrame();
                    divider1.setFrameShape(QFrame.Shape.VLine);
                    divider1.setFrameShadow(QFrame.Shadow.Sunken)
                    seat2 = QWidget();
                    seat2.setStyleSheet("background-color: lightyellow; border-radius: 3px;")
                    divider2 = QFrame();
                    divider2.setFrameShape(QFrame.Shape.VLine);
                    divider2.setFrameShadow(QFrame.Shadow.Sunken)
                    seat3 = QWidget();
                    seat3.setStyleSheet("background-color: lightyellow; border-radius: 3px;")
                    divider3 = QFrame();
                    divider3.setFrameShape(QFrame.Shape.VLine);
                    divider3.setFrameShadow(QFrame.Shadow.Sunken)
                    seat4 = QWidget();
                    seat4.setStyleSheet("background-color: lightyellow; border-radius: 3px;")

                    # Tüm elemanları sırasıyla layout'a ekle
                    desk_layout.addWidget(seat1)
                    desk_layout.addWidget(divider1)
                    desk_layout.addWidget(seat2)
                    desk_layout.addWidget(divider2)
                    desk_layout.addWidget(seat3)
                    desk_layout.addWidget(divider3)
                    desk_layout.addWidget(seat4)

                    desk_group_frame.setFixedSize(200, 40)  # 4'lü sıra için boyutu ayarla
                # --- DÜZELTME SONU ---

                else:  # "Tekli" veya diğer tüm durumlar
                    seat1 = QWidget()
                    seat1.setStyleSheet("background-color: lightcoral; border-radius: 3px;")
                    desk_layout.addWidget(seat1)
                    desk_group_frame.setFixedSize(50, 40)

                main_layout.addWidget(desk_group_frame, satir, sutun, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)