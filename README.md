# Sınav Takvimi Oluşturucu

Ders, öğrenci ve derslik verilerinden sınav programı ve oturma planı üreten PyQt6 masaüstü uygulaması. Çakışmaları azaltan planlama akışını Excel içe/dışa aktarma ve PDF raporlama ile tamamlar.

## Özellikler

- Kullanıcı giriş ekranı ve masaüstü yönetim paneli
- Excel dosyalarından ders ve öğrenci verisi okuma
- Sınav takvimi oluşturma
- Derslik ve oturma planı hazırlama
- Sonuçları Excel ve PDF olarak raporlama
- PostgreSQL üzerinde kayıt yönetimi

## Teknolojiler

- Python 3 ve PyQt6
- Pandas ve OpenPyXL
- PostgreSQL / psycopg2
- ReportLab

## Kurulum

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Uygulamayı çalıştırmadan önce `database.py` içindeki PostgreSQL bağlantı ayarlarını kendi geliştirme ortamınıza göre yapılandırın.

## Beklenen Veri Akışı

1. Ders ve öğrenci listelerini Excel dosyalarından yükleyin.
2. Derslikleri ve sınav parametrelerini tanımlayın.
3. Takvim oluşturma algoritmasını çalıştırın.
4. Sonuçları kontrol edip oturma planlarını PDF olarak dışa aktarın.

## Proje Yapısı

```text
ui/                         PyQt6 ekranları
takvim_algoritmasi.py       Sınav planlama mantığı
oturma_plani_algoritmasi.py Oturma düzeni üretimi
excel_parser.py             Excel veri aktarımı
pdf_reporter.py             PDF çıktıları
database.py                 PostgreSQL işlemleri
```
