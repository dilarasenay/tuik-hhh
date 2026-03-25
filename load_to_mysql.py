import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_TABLE = os.getenv("MYSQL_TABLE")
CSV_FILE = os.getenv("CSV_FILE")

engine = create_engine(
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

def make_unique_columns(columns):
    seen = {}
    new_cols = []

    for col in columns:
        col = str(col).strip()
        col = col.replace(" ", "_")
        col = "".join(ch for ch in col if ch.isalnum() or ch == "_")
        col = col[:60]

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 0

        new_cols.append(col)

    return new_cols

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        try:
            if df[col].dtype == "int64":
                df[col] = pd.to_numeric(df[col], downcast="integer")
            elif df[col].dtype == "float64":
                df[col] = pd.to_numeric(df[col], downcast="float")
        except Exception:
            pass
    return df

def main():
    print("CSV okunuyor...")
    df = pd.read_csv(CSV_FILE, low_memory=False)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Kolon isimlerini temizle + benzersiz yap
    df.columns = make_unique_columns(df.columns)

    # Tamamen boş kolonları sil
    df = df.dropna(axis=1, how="all")

    df = optimize_dtypes(df)

    print(f"Satır sayısı: {df.shape[0]}")
    print(f"Kolon sayısı: {df.shape[1]}")

    print("İlk 15 kolon:")
    print(df.columns[:15].tolist())

    print("MySQL'e yazılıyor...")

    df.to_sql(
        name=MYSQL_TABLE,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("Aktarım tamamlandı.")

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {MYSQL_TABLE}"))
        total = result.scalar()
        print(f"MySQL içindeki toplam kayıt: {total}")

if __name__ == "__main__":
    main()