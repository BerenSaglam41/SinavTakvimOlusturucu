from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class GorsellestirmeDialog(QDialog):
    def __init__(self, derslik_detaylari, parent=None):
        super().__init__(parent)

        # Gelen veriyi değişkenlere ata
        derslik_adi = derslik_detaylari[3]
        enine_sira = derslik_detaylari[5]  # Sütun sayısı
        boyuna_sira = derslik_detaylari[6]  # Satır sayısı

        self.setWindowTitle(f"Oturma Düzeni: {derslik_adi}")

        # Ana layout olarak Grid (Izgara) Layout kullan
        layout = QGridLayout(self)
        layout.setSpacing(10)  # Sıralar arasına boşluk koy

        # Proje belgesi: Satır x Sütunluk bir düzen çizilir.
        # Bu döngü, her bir sırayı temsil eden kutucuklar oluşturur.
        for satir in range(boyuna_sira):
            for sutun in range(enine_sira):
                sira = QFrame()
                sira.setFrameShape(QFrame.Shape.Box)
                sira.setFixedSize(50, 30)  # Her bir sıranın boyutu
                sira.setStyleSheet("background-color: lightblue; border: 1px solid black;")

                # Etiket ekleyerek sıra numarasını yazdırabiliriz (isteğe bağlı)
                # etiket = QLabel(f"{satir+1}-{sutun+1}")
                # etiket.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # sira_layout = QVBoxLayout(sira)
                # sira_layout.addWidget(etiket)

                layout.addWidget(sira, satir, sutun)

        self.setLayout(layout)