import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# ==========================================
# ENV AYARLARI
# ==========================================
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "panel_db")
MYSQL_TABLE = os.getenv("MYSQL_TABLE", "panel_data")

# CSV yolu
CSV_FILE = "data/panel_veri.csv"

# ==========================================
# ENGINE
# ==========================================
def create_db_engine(with_database=True):
    if with_database:
        url = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    else:
        url = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"
    return create_engine(url)

# ==========================================
# DATABASE OLUŞTUR
# ==========================================
def ensure_database():
    engine = create_db_engine(with_database=False)
    with engine.connect() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.commit()
    print(f"Veritabanı hazır: {MYSQL_DATABASE}")

# ==========================================
# CSV OKU
# ==========================================
def read_csv_file():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"CSV dosyası bulunamadı: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE, low_memory=False)
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]

    # Baştaki isimsiz index kolonu varsa sil
    unnamed_cols = [col for col in df.columns if str(col).startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    print(f"CSV okundu: {CSV_FILE}")
    print(f"Satır sayısı: {df.shape[0]}")
    print(f"Sütun sayısı: {df.shape[1]}")
    print("İlk 10 sütun:", df.columns[:10].tolist())

    return df

# ==========================================
# MYSQL'E YÜKLE
# ==========================================
def load_to_mysql():
    ensure_database()
    df = read_csv_file()
    engine = create_db_engine(with_database=True)

    df.to_sql(
        name=MYSQL_TABLE,
        con=engine,
        if_exists="replace",   # tablo varsa silip yeniden oluşturur
        index=False,
        chunksize=10000,
        method="multi"
    )

    print(f"Veri başarıyla yüklendi.")
    print(f"Tablo adı: {MYSQL_TABLE}")

    # kontrol
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {MYSQL_TABLE}"))
        count = result.scalar()
        print(f"MySQL içindeki toplam kayıt sayısı: {count}")

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    try:
        load_to_mysql()
    except Exception as e:
        print("HATA OLUŞTU:")
        print(e)