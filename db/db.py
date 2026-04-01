import os
import pandas as pd
from config.config import DATA_PATH

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH, low_memory=False)

    # Kolon isimlerini temizle
    df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]

    # Gereksiz unnamed kolonları sil
    unnamed_cols = [col for col in df.columns if str(col).startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    # Tekrarlayan kolon adlarında ilkini bırak, diğerlerini sil
    df = df.loc[:, ~df.columns.duplicated()]

    # İstersen açık açık bu iki gelir kolonunu da tamamen kaldır
    cols_to_drop = [
        "GELIR_NAKDI_ORTAKCI",
        "GELIR_AYNI_TOPLAM"
    ]
    existing_drop_cols = [col for col in cols_to_drop if col in df.columns]
    if existing_drop_cols:
        df = df.drop(columns=existing_drop_cols)

    return df