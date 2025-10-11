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