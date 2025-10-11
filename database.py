import psycopg2
from psycopg2.extras import execute_batch # BU SATIRI EKLE

DB_CONNECTION_STRING = "postgresql://postgres.zmmnhfizjtgxjzwjxdar:05314039191qwE@aws-1-us-east-2.pooler.supabase.com:5432/postgres"


def get_connection():
    """Veritabanı bağlantısı oluşturan ve döndüren fonksiyon."""
    try:
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        return conn
    except psycopg2.OperationalError as e:
        print(f"HATA: Veritabanına bağlanılamadı. -> {e}")
        return None

def derslik_sil(derslik_id):
    """Verilen ID'ye sahip dersliği veritabanından siler."""
    conn = get_connection()
    if conn is None:
        return False, "Veritabanı bağlantısı kurulamadı."

    sql_komutu = "DELETE FROM Derslikler WHERE derslik_id = %s;"

    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, (derslik_id,))
        conn.commit()
        # Silme işlemi başarılı olduysa ve en az bir satır etkilendiyse
        if cur.rowcount > 0:
            return True, "Derslik başarıyla silindi."
        else:
            return False, "Silinecek derslik bulunamadı."
        cur.close()
    except Exception as e:
        conn.rollback()  # Hata durumunda işlemi geri al
        return False, f"Derslik silinirken hata oluştu: {e}"
    finally:
        if conn is not None:
            conn.close()

def derslikleri_getir(bolum_id):
    """Belirli bir bölüme ait tüm derslikleri veritabanından çeker."""
    conn = get_connection()
    if conn is None:
        return []

    sql_komutu = "SELECT derslik_id, derslik_kodu, derslik_adi, kapasite FROM Derslikler WHERE bolum_id = %s ORDER BY derslik_kodu;"

    derslikler = []
    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, (bolum_id,))
        derslikler = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"HATA: Derslikler getirilirken bir sorun oluştu. -> {e}")
    finally:
        if conn is not None:
            conn.close()

    return derslikler

def derslik_ekle(derslik_bilgileri):
    """Veritabanına yeni bir derslik kaydı ekler."""
    conn = get_connection()
    if conn is None:
        return False, "Veritabanı bağlantısı kurulamadı."

    sql_komutu = """
                 INSERT INTO Derslikler (bolum_id, derslik_kodu, derslik_adi, kapasite,
                                         enine_sira_sayisi, boyuna_sira_sayisi, sira_yapisi)
                 VALUES (%(bolum_id)s, %(derslik_kodu)s, %(derslik_adi)s, %(kapasite)s,
                         %(enine_sira)s, %(boyuna_sira)s, %(sira_yapisi)s); \
                 """

    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, derslik_bilgileri)
        conn.commit()
        cur.close()
        return True, "Derslik başarıyla eklendi."
    except Exception as e:
        conn.rollback()  # Hata durumunda işlemi geri al
        return False, f"Derslik eklenirken hata oluştu: {e}"
    finally:
        if conn is not None:
            conn.close()

def derslik_detay_getir(derslik_id):
    """Verilen ID'ye sahip tek bir dersliğin tüm bilgilerini çeker."""
    conn = get_connection()
    if conn is None:
        return None

    sql_komutu = "SELECT * FROM Derslikler WHERE derslik_id = %s;"
    derslik_detay = None
    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, (derslik_id,))
        derslik_detay = cur.fetchone()
        cur.close()
    except Exception as e:
        print(f"HATA: Derslik detayı getirilirken sorun oluştu: {e}")
    finally:
        if conn is not None:
            conn.close()
    return derslik_detay

def derslik_guncelle(derslik_bilgileri):
    """Verilen ID'ye sahip dersliğin bilgilerini günceller."""
    conn = get_connection()
    if conn is None:
        return False, "Veritabanı bağlantısı kurulamadı."

    sql_komutu = """
                 UPDATE Derslikler \
                 SET derslik_kodu       = %(derslik_kodu)s, \
                     derslik_adi        = %(derslik_adi)s, \
                     kapasite           = %(kapasite)s, \
                     enine_sira_sayisi  = %(enine_sira)s, \
                     boyuna_sira_sayisi = %(boyuna_sira)s, \
                     sira_yapisi        = %(sira_yapisi)s
                 WHERE derslik_id = %(derslik_id)s; \
                 """

    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, derslik_bilgileri)
        conn.commit()
        cur.close()
        return True, "Derslik başarıyla güncellendi."
    except Exception as e:
        conn.rollback()
        return False, f"Derslik güncellenirken hata oluştu: {e}"
    finally:
        if conn is not None:
            conn.close()

def kullanici_dogrula(email, sifre):
    """Verilen email ve şifre ile kullanıcıyı doğrular, kullanıcı bilgilerini döndürür."""
    conn = get_connection()
    if conn is None:
        return None

    user_data = None
    try:
        cur = conn.cursor()

        # Kullanıcı girişi için SQL sorgusu [cite: 24]
        sql_komutu = "SELECT kullanici_id, email, rol, bolum_id FROM Kullanicilar WHERE email = %s AND sifre = %s;"

        cur.execute(sql_komutu, (email, sifre))
        user_data = cur.fetchone()  # Eğer kullanıcı varsa bilgilerini alır, yoksa None döner.

        cur.close()
    except Exception as e:
        print(f"HATA: Kullanıcı doğrulanırken bir sorun oluştu. -> {e}")
    finally:
        if conn is not None:
            conn.close()

    return user_data

def dersleri_sil_ve_ekle(dersler_listesi, bolum_id):
    """
    Önce ilgili bölüme ait tüm eski dersleri siler, ardından
    yeni ders listesini toplu olarak ekler. (Tavsiye edilen yöntem)
    """
    conn = get_connection()
    if conn is None:
        return False, "Veritabanı bağlantısı kurulamadı."

    # SQL komutları
    delete_sql = "DELETE FROM Dersler WHERE bolum_id = %s;"
    insert_sql = """
                 INSERT INTO Dersler (bolum_id, ders_kodu, ders_adi, ogretim_uyesi, sinif, yapi)
                 VALUES (%(bolum_id)s, %(ders_kodu)s, %(ders_adi)s, %(ogretim_uyesi)s, %(sinif)s, %(yapi)s); \
                 """

    try:
        cur = conn.cursor()

        # 1. Adım: Önce o bölüme ait eski dersleri sil
        print(f"{bolum_id} ID'li bölümün eski dersleri siliniyor...")
        cur.execute(delete_sql, (bolum_id,))
        print(f"{cur.rowcount} adet eski ders silindi.")

        # 2. Adım: Yeni dersleri ekle
        print(f"{len(dersler_listesi)} adet yeni ders ekleniyor...")
        for ders in dersler_listesi:
            ders['bolum_id'] = bolum_id
            cur.execute(insert_sql, ders)

        conn.commit()
        cur.close()
        return True, f"{len(dersler_listesi)} adet yeni ders başarıyla yüklendi. (Eskiler silindi)"
    except Exception as e:
        conn.rollback()
        return False, f"İşlem sırasında veritabanı hatası oluştu: {e}"
    finally:
        if conn is not None:
            conn.close()

def ogrencileri_sil_ve_ekle(kayitlar_listesi, bolum_id):
    """
    (Optimize Edilmiş Sürüm)
    İlgili bölüme ait eski öğrencileri ve ders kayıtlarını siler.
    Ardından yeni öğrenci listesini ve ders kayıtlarını toplu olarak (batch) ekler.
    """
    conn = get_connection()
    if conn is None:
        return False, "Veritabanı bağlantısı kurulamadı."

    try:
        cur = conn.cursor()

        # 1. Adım: Önce o bölüme ait tüm eski öğrencileri sil.
        # CASCADE sayesinde bu öğrencilere ait ders kayıtları da OgrenciDersKayitlari tablosundan otomatik silinir.
        print(f"{bolum_id} ID'li bölümün eski öğrencileri siliniyor...")
        cur.execute("DELETE FROM Ogrenciler WHERE bolum_id = %s;", (bolum_id,))
        print(f"{cur.rowcount} eski öğrenci silindi.")

        # 2. Adım: Excel'den gelen veriyi Python içinde hazırla
        # a) Tekrarları önlemek için benzersiz öğrencileri bir sözlükte topla
        benzersiz_ogrenciler = {
            kayit['ogrenci_no']: {
                'ogrenci_no': kayit['ogrenci_no'],
                'ad_soyad': kayit['ad_soyad'],
                'sinif': kayit['sinif']
            }
            for kayit in kayitlar_listesi
        }.values()  # .values() ile sadece öğrenci bilgilerini al

        # b) O bölüme ait tüm derslerin ID'lerini tek bir sorguyla alıp hafızaya yükle
        cur.execute("SELECT ders_kodu, ders_id FROM Dersler WHERE bolum_id = %s;", (bolum_id,))
        ders_idler_map = dict(cur.fetchall())  # {'CSE101': 1, 'BLM3001': 5}

        # 3. Adım: Benzersiz öğrencileri 'Ogrenciler' tablosuna toplu olarak ekle
        print(f"{len(benzersiz_ogrenciler)} benzersiz öğrenci toplu olarak ekleniyor...")
        insert_ogrenci_sql = "INSERT INTO Ogrenciler (bolum_id, ogrenci_no, ad_soyad, sinif) VALUES (%s, %s, %s, %s);"
        # execute_batch için veri listesi hazırla
        ogrenciler_data = [
            (bolum_id, ogr['ogrenci_no'], ogr['ad_soyad'], ogr['sinif'])
            for ogr in benzersiz_ogrenciler
        ]
        execute_batch(cur, insert_ogrenci_sql, ogrenciler_data)

        # 4. Adım: Yeni eklenen öğrencilerin ID'lerini numaralarıyla eşleştirmek için veritabanından geri al
        cur.execute("SELECT ogrenci_no, ogrenci_id FROM Ogrenciler WHERE bolum_id = %s;", (bolum_id,))
        ogrenci_idler_map = dict(cur.fetchall())  # {'2025001': 101, '2025002': 102}

        # 5. Adım: 'OgrenciDersKayitlari' tablosu için veriyi hazırla
        ders_kayit_data = []
        for kayit in kayitlar_listesi:
            ogrenci_no = kayit['ogrenci_no']
            ders_kodu = kayit['ders_kodu']

            ogrenci_id = ogrenci_idler_map.get(ogrenci_no)
            ders_id = ders_idler_map.get(ders_kodu)

            if ogrenci_id and ders_id:  # Öğrenci ve ders ID'leri bulunduysa
                ders_kayit_data.append((ogrenci_id, ders_id))
            else:
                print(f"UYARI: {ogrenci_no} veya {ders_kodu} için ID bulunamadı, kayıt atlanıyor.")

        # 6. Adım: Ders kayıtlarını 'OgrenciDersKayitlari' tablosuna toplu olarak ekle
        print(f"{len(ders_kayit_data)} ders kaydı toplu olarak ekleniyor...")
        insert_kayit_sql = "INSERT INTO OgrenciDersKayitlari (ogrenci_id, ders_id) VALUES (%s, %s);"
        execute_batch(cur, insert_kayit_sql, ders_kayit_data)

        conn.commit()
        cur.close()
        return True, f"{len(benzersiz_ogrenciler)} öğrenci ve {len(ders_kayit_data)} ders kaydı başarıyla yüklendi."

    except Exception as e:
        conn.rollback()
        return False, f"İşlem sırasında veritabanı hatası oluştu: {e}"
    finally:
        if conn is not None:
            conn.close()

def ogrenci_derslerini_getir(ogrenci_no, bolum_id):
    """Verilen öğrenci numarasına göre öğrencinin adını ve aldığı dersleri döndürür."""
    conn = get_connection()
    if conn is None:
        return None, []

    # SQL'de tabloları birleştirerek (JOIN) öğrencinin derslerini buluyoruz.
    sql_komutu = """
        SELECT o.ad_soyad, d.ders_kodu, d.ders_adi 
        FROM Ogrenciler o
        JOIN OgrenciDersKayitlari odk ON o.ogrenci_id = odk.ogrenci_id
        JOIN Dersler d ON odk.ders_id = d.ders_id
        WHERE o.ogrenci_no = %s AND o.bolum_id = %s;
    """
    ogrenci_adi = None
    dersler = []
    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, (ogrenci_no, bolum_id))
        rows = cur.fetchall()
        if rows:
            ogrenci_adi = rows[0][0] # İlk satırın ilk sütunu öğrencinin adıdır
            dersler = [f"{row[1]} - {row[2]}" for row in rows] # Ders kodu ve adını birleştir
        cur.close()
    except Exception as e:
        print(f"HATA: Öğrenci dersleri getirilirken sorun oluştu: {e}")
    finally:
        if conn is not None:
            conn.close()
    return ogrenci_adi, dersler

def bolumun_derslerini_getir(bolum_id):
    """Belirli bir bölüme ait tüm dersleri (ID, Kod, Ad) listesi olarak döndürür."""
    conn = get_connection()
    if conn is None: return []
    sql_komutu = "SELECT ders_id, ders_kodu, ders_adi FROM Dersler WHERE bolum_id = %s ORDER BY ders_kodu;"
    dersler = []
    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, (bolum_id,))
        dersler = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"HATA: Bölüm dersleri getirilirken sorun oluştu: {e}")
    finally:
        if conn is not None:
            conn.close()
    return dersler

def dersi_alan_ogrencileri_getir(ders_id):
    """Verilen ders ID'sine göre o dersi alan tüm öğrencileri döndürür."""
    conn = get_connection()
    if conn is None: return []
    sql_komutu = """
        SELECT o.ogrenci_no, o.ad_soyad 
        FROM Ogrenciler o 
        JOIN OgrenciDersKayitlari odk ON o.ogrenci_id = odk.ogrenci_id 
        WHERE odk.ders_id = %s ORDER BY o.ogrenci_no;
    """
    ogrenciler = []
    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, (ders_id,))
        ogrenciler = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"HATA: Dersi alan öğrenciler getirilirken sorun oluştu: {e}")
    finally:
        if conn is not None:
            conn.close()
    return ogrenciler

def ders_verisi_var_mi(bolum_id):
    """Belirtilen bölüme ait en az bir ders kaydı olup olmadığını kontrol eder."""
    conn = get_connection()
    if conn is None: return False

    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Dersler WHERE bolum_id = %s;", (bolum_id,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0  # Eğer satır sayısı 0'dan büyükse True döner
    except Exception as e:
        print(f"HATA: Ders verisi kontrol edilirken sorun oluştu: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

def ogrenci_verisi_var_mi(bolum_id):
    """Belirtilen bölüme ait en az bir öğrenci kaydı olup olmadığını kontrol eder."""
    conn = get_connection()
    if conn is None: return False

    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Ogrenciler WHERE bolum_id = %s;", (bolum_id,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0  # Eğer satır sayısı 0'dan büyükse True döner
    except Exception as e:
        print(f"HATA: Öğrenci verisi kontrol edilirken sorun oluştu: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

            def sinav_programini_kaydet(program, bolum_id, sinav_turu):
                """Oluşturulan sınav programını veritabanı tablolarına kaydeder."""
                conn = get_connection()
                if conn is None: return False, "Veritabanı bağlantısı kurulamadı."

                try:
                    cur = conn.cursor()

                    # 1. Adım: O bölüme ait eski sınav programını temizle
                    cur.execute("DELETE FROM SinavProgrami WHERE bolum_id = %s AND sinav_turu = %s;",
                                (bolum_id, sinav_turu))

                    # 2. Adım: Yeni programı kaydet
                    for ders_id, info in program.items():
                        # a) SinavProgrami tablosuna ana kaydı ekle ve yeni sinav_id'yi al
                        sql_sinav_ekle = """
                                         INSERT INTO SinavProgrami (bolum_id, ders_id, sinav_turu, tarih, saat, sure)
                                         VALUES (%s, %s, %s, %s, %s, %s) RETURNING sinav_id; \
                                         """
                        # Varsayılan süreyi şimdilik 75 dk alıyoruz, bu daha sonra arayüzden gelen süre ile değiştirilebilir.
                        cur.execute(sql_sinav_ekle, (bolum_id, ders_id, sinav_turu, info['tarih'], info['saat'], 75))
                        yeni_sinav_id = cur.fetchone()[0]

                        # b) O sınava atanan her dersliği SinavDerslikAtamalari tablosuna ekle
                        for derslik in info['derslikler']:
                            derslik_id = derslik['id']
                            sql_atama_ekle = "INSERT INTO SinavDerslikAtamalari (sinav_id, derslik_id) VALUES (%s, %s);"
                            cur.execute(sql_atama_ekle, (yeni_sinav_id, derslik_id))

                    conn.commit()
                    cur.close()
                    return True, "Sınav programı başarıyla veritabanına kaydedildi."
                except Exception as e:
                    conn.rollback()
                    return False, f"Program kaydedilirken veritabanı hatası oluştu: {e}"
                finally:
                    if conn is not None:
                        conn.close()

def sinav_programini_kaydet(program, bolum_id, sinav_turu):
    """Oluşturulan sınav programını veritabanı tablolarına kaydeder."""
    conn = get_connection()
    if conn is None: return False, "Veritabanı bağlantısı kurulamadı."

    try:
        cur = conn.cursor()

        # 1. Adım: O bölüme ait eski sınav programını temizle
        cur.execute("DELETE FROM SinavProgrami WHERE bolum_id = %s AND sinav_turu = %s;", (bolum_id, sinav_turu))

        # 2. Adım: Yeni programı kaydet
        for ders_id, info in program.items():
            # a) SinavProgrami tablosuna ana kaydı ekle ve yeni sinav_id'yi al
            sql_sinav_ekle = """
                             INSERT INTO SinavProgrami (bolum_id, ders_id, sinav_turu, tarih, saat, sure)
                             VALUES (%s, %s, %s, %s, %s, %s) RETURNING sinav_id; \
                             """
            # Varsayılan süreyi şimdilik 75 dk alıyoruz, bu daha sonra arayüzden gelen süre ile değiştirilebilir.
            cur.execute(sql_sinav_ekle, (bolum_id, ders_id, sinav_turu, info['tarih'], info['saat'], 75))
            yeni_sinav_id = cur.fetchone()[0]

            # b) O sınava atanan her dersliği SinavDerslikAtamalari tablosuna ekle
            for derslik in info['derslikler']:
                derslik_id = derslik['id']
                sql_atama_ekle = "INSERT INTO SinavDerslikAtamalari (sinav_id, derslik_id) VALUES (%s, %s);"
                cur.execute(sql_atama_ekle, (yeni_sinav_id, derslik_id))

        conn.commit()
        cur.close()
        return True, "Sınav programı başarıyla veritabanına kaydedildi."
    except Exception as e:
        conn.rollback()
        return False, f"Program kaydedilirken veritabanı hatası oluştu: {e}"
    finally:
        if conn is not None:
            conn.close()

            # ... (dosyanın üstündeki diğer fonksiyonlar aynı kalacak) ...

            def sinav_programi_var_mi(bolum_id):
                """Belirtilen bölüme ait en az bir sınav kaydı olup olmadığını kontrol eder."""
                conn = get_connection()
                if conn is None: return False
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM SinavProgrami WHERE bolum_id = %s;", (bolum_id,))
                    count = cur.fetchone()[0]
                    cur.close()
                    return count > 0
                except Exception as e:
                    print(f"HATA: Sınav programı varlığı kontrol edilirken sorun oluştu: {e}")
                    return False
                finally:
                    if conn is not None:
                        conn.close()

            def get_sinav_listesi(bolum_id):
                """Belirtilen bölüme ait, oluşturulmuş tüm sınavları listeler."""
                conn = get_connection()
                if conn is None: return []
                sql_komutu = """
                             SELECT sp.sinav_id, d.ders_kodu, d.ders_adi, sp.tarih, sp.saat
                             FROM SinavProgrami sp
                                      JOIN Dersler d ON sp.ders_id = d.ders_id
                             WHERE sp.bolum_id = %s
                             ORDER BY sp.tarih, sp.saat; \
                             """
                sinavlar = []
                try:
                    cur = conn.cursor()
                    cur.execute(sql_komutu, (bolum_id,))
                    sinavlar = cur.fetchall()
                    cur.close()
                except Exception as e:
                    print(f"HATA: Sınav listesi getirilirken sorun oluştu: {e}")
                finally:
                    if conn is not None:
                        conn.close()
                return sinavlar

def sinav_programi_var_mi(bolum_id):
    """Belirtilen bölüme ait en az bir sınav kaydı olup olmadığını kontrol eder."""
    conn = get_connection()
    if conn is None: return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM SinavProgrami WHERE bolum_id = %s;", (bolum_id,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    except Exception as e:
        print(f"HATA: Sınav programı varlığı kontrol edilirken sorun oluştu: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

def get_sinav_listesi(bolum_id):
    """Belirtilen bölüme ait, oluşturulmuş tüm sınavları listeler."""
    conn = get_connection()
    if conn is None: return []
    sql_komutu = """
        SELECT sp.sinav_id, d.ders_kodu, d.ders_adi, sp.tarih, sp.saat
        FROM SinavProgrami sp
        JOIN Dersler d ON sp.ders_id = d.ders_id
        WHERE sp.bolum_id = %s
        ORDER BY sp.tarih, sp.saat;
    """
    sinavlar = []
    try:
        cur = conn.cursor()
        cur.execute(sql_komutu, (bolum_id,))
        sinavlar = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"HATA: Sınav listesi getirilirken sorun oluştu: {e}")
    finally:
        if conn is not None:
            conn.close()
    return sinavlar

def get_sinav_detaylari_for_plan(sinav_id):
    """Oturma planı için seçilen sınavın tüm detaylarını çeker."""
    conn = get_connection()
    if conn is None: return None, None

    # 1. Sınava giren öğrencileri al
    ogrenciler_sql = """
                     SELECT o.ogrenci_id, o.ogrenci_no, o.ad_soyad
                     FROM Ogrenciler o
                              JOIN OgrenciDersKayitlari odk ON o.ogrenci_id = odk.ogrenci_id
                              JOIN SinavProgrami sp ON odk.ders_id = sp.ders_id
                     WHERE sp.sinav_id = %s; \
                     """

    # 2. Sınavın yapılacağı derslikleri ve özelliklerini al
    derslikler_sql = """
                     SELECT d.derslik_id, d.derslik_adi, d.enine_sira_sayisi, d.boyuna_sira_sayisi, d.sira_yapisi
                     FROM Derslikler d
                              JOIN SinavDerslikAtamalari sda ON d.derslik_id = sda.derslik_id
                     WHERE sda.sinav_id = %s; \
                     """

    ogrenciler = []
    derslikler = []
    try:
        cur = conn.cursor()
        cur.execute(ogrenciler_sql, (sinav_id,))
        ogrenciler = cur.fetchall()
        cur.execute(derslikler_sql, (sinav_id,))
        derslikler = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"HATA: Sınav detayları getirilirken sorun oluştu: {e}")
    finally:
        if conn is not None:
            conn.close()

    return ogrenciler, derslikler

def oturma_planini_kaydet(sinav_id, plan):
    """Oluşturulan oturma planını veritabanına kaydeder."""
    conn = get_connection()
    if conn is None: return False, "Veritabanı bağlantısı kurulamadı."

    try:
        cur = conn.cursor()
        # Önce bu sınava ait eski planı temizle
        cur.execute("DELETE FROM OturmaPlanlari WHERE sinav_id = %s;", (sinav_id,))

        # Yeni planı toplu olarak ekle
        sql_insert = "INSERT INTO OturmaPlanlari (sinav_id, ogrenci_id, derslik_id, sira_no, sutun_no) VALUES (%s, %s, %s, %s, %s);"

        from psycopg2.extras import execute_batch  # Bu importu fonksiyon içinde yapabiliriz
        execute_batch(cur, sql_insert, plan)

        conn.commit()
        cur.close()
        return True, "Oturma planı başarıyla veritabanına kaydedildi."
    except Exception as e:
        conn.rollback()
        return False, f"Oturma planı kaydedilirken hata oluştu: {e}"
    finally:
        if conn is not None:
            conn.close()