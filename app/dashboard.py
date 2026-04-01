import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sys
import os
import html

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db.db import load_data

st.set_page_config(
    page_title="TÜİK Sağlık Harcaması Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================
if "last_filter_signature" not in st.session_state:
    st.session_state.last_filter_signature = None

if "alert_open" not in st.session_state:
    st.session_state.alert_open = False

if "alert_data" not in st.session_state:
    st.session_state.alert_data = {
        "title": "",
        "subtitle": "",
        "detail": "",
        "risk": "Yüksek Risk",
        "tag2": "Dar Örneklem",
        "tag3": "Filtre Kaynaklı İçgörü"
    }

# =========================================================
# RENKLER
# =========================================================
PRIMARY_GREEN = "#22c55e"
SOFT_YELLOW = "#facc15"
SOFT_BLUE = "#38bdf8"
SOFT_ORANGE = "#f59e0b"
SOFT_CYAN = "#06b6d4"
SOFT_INDIGO = "#6366f1"
SOFT_EMERALD = "#10b981"
TEXT_DARK = "#0f172a"
TEXT_MID = "#334155"
TEXT_SOFT = "#475569"
GRID_COLOR = "rgba(148,163,184,0.16)"

# =========================================================
# MAPPING'LER
# =========================================================
CINSIYET_MAP = {
    1: "Erkek",
    2: "Kadın"
}

OKUL_BITEN_MAP = {
    0: "Bir okul bitirmedi",
    1: "İlkokul",
    21: "Genel ortaokul",
    22: "Mesleki veya teknik ortaokul",
    23: "İlköğretim",
    31: "Genel lise",
    32: "Mesleki veya teknik lise",
    4: "2 veya 3 yıllık yüksekokul",
    5: "4 yıllık yüksekokul veya fakülte",
    61: "5 veya 6 yıllık fakülte",
    62: "Yüksek lisans",
    7: "Doktora"
}

SAGLIK_SIGORTA_MAP = {
    11: "SGK - SSK (4A)",
    12: "SGK - Bağ-Kur (4B)",
    13: "SGK - Emekli Sandığı (4C)",
    14: "Banka Sandığı / Vakıf",
    15: "Özel Sağlık Sigortası",
    16: "GSS (Yeşil Kart)",
    2: "Sigorta Yok"
}

HBS_KOD5_MAP = {
    6110: "Eczacılık ürünleri",
    6121: "Gebelik testleri ve gebelik önleyici mekanik cihazlar",
    6129: "Diğer tıbbi ürünler",
    6131: "Düzeltici gözlükler ve kontak lensler",
    6132: "İşitme cihazları",
    6133: "Tedavi amaçlı alet ve ekipmanların onarımı",
    6139: "Diğer tedavi amaçlı alet ve ekipmanlar",
    6211: "Pratisyen hekimlik",
    6212: "Uzman hekimlik",
    6220: "Diş hekimliği hizmetleri",
    6231: "Tıbbi analiz laboratuvarı ve röntgen hizmetleri",
    6232: "Kaplıca, ambulans ve tedavi amaçlı ekipman kiralama",
    6239: "Diğer paramedikal hizmetler",
    6300: "Hastane hizmetleri"
}

MEDENI_DURUM_MAP = {
    1: "Hiç evlenmedi",
    2: "Evli",
    3: "Boşandı",
    4: "Eşi öldü"
}

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(56, 189, 248, 0.20), transparent 20%),
            radial-gradient(circle at 92% 10%, rgba(250, 204, 21, 0.20), transparent 22%),
            radial-gradient(circle at 85% 85%, rgba(34, 197, 94, 0.16), transparent 22%),
            radial-gradient(circle at 15% 88%, rgba(99, 102, 241, 0.14), transparent 18%),
            linear-gradient(135deg, #f7fbff 0%, #f4fff8 38%, #fffef6 72%, #f7fbff 100%);
        color: #14213d;
    }

    .block-container {
        max-width: 1520px;
        padding-top: 0.85rem !important;
        padding-bottom: 2.3rem;
        padding-left: 1.6rem;
        padding-right: 1.6rem;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0rem !important;
    }

    div[data-testid="stToolbar"] {
        top: 0.35rem !important;
        right: 0.55rem !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(248,250,252,0.97) 0%, rgba(242,247,255,0.96) 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.18);
        width: 275px !important;
        min-width: 275px !important;
        box-shadow: 6px 0 30px rgba(148,163,184,0.08);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 0.8rem !important;
    }

    [data-testid="collapsedControl"],
    button[kind="header"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarNavCollapseButton"] {
        display: none !important;
    }

    .hero-card {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.78) 0%, rgba(240,249,255,0.90) 30%, rgba(254,252,232,0.86) 65%, rgba(236,253,245,0.84) 100%);
        border: 1px solid rgba(255,255,255,0.65);
        border-radius: 30px;
        padding: 30px 34px;
        box-shadow:
            0 20px 55px rgba(148, 163, 184, 0.13),
            0 8px 28px rgba(56, 189, 248, 0.08),
            inset 0 1px 0 rgba(255,255,255,0.85);
        margin-top: 0.1rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(14px);
    }

    .hero-card::before {
        content: "";
        position: absolute;
        top: -80px;
        right: -80px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(56,189,248,0.18) 0%, transparent 70%);
        border-radius: 50%;
    }

    .hero-card::after {
        content: "";
        position: absolute;
        bottom: -90px;
        left: -60px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(250,204,21,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }

    .hero-title {
        position: relative;
        z-index: 2;
        font-size: 2.2rem;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 0.5rem;
        line-height: 1.06;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        position: relative;
        z-index: 2;
        font-size: 1rem;
        color: #334155;
        line-height: 1.7;
        max-width: 980px;
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 900;
        color: #0f172a;
        margin-top: 0.7rem;
        margin-bottom: 0.9rem;
        letter-spacing: -0.2px;
    }

    .mini-card, .kpi-card {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.78), rgba(255,255,255,0.58));
        border: 1px solid rgba(255,255,255,0.72);
        border-radius: 24px;
        padding: 19px 21px;
        box-shadow:
            0 16px 34px rgba(148,163,184,0.10),
            0 4px 18px rgba(56,189,248,0.04);
        backdrop-filter: blur(12px);
    }

    .mini-label, .kpi-label {
        font-size: 0.92rem;
        color: #64748b;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    .mini-value, .kpi-value {
        font-size: 1.95rem;
        font-weight: 900;
        color: #0f172a;
        line-height: 1.03;
        letter-spacing: -0.6px;
    }

    .panel-title {
        font-size: 1.05rem;
        font-weight: 850;
        color: #0f172a;
        margin-bottom: 0.65rem;
    }

    .insight-card {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.84), rgba(254,249,195,0.76), rgba(224,242,254,0.72));
        border: 1px solid rgba(250, 204, 21, 0.24);
        border-left: 5px solid #facc15;
        border-radius: 22px;
        padding: 18px 20px;
        color: #1e293b;
        line-height: 1.8;
        box-shadow:
            0 15px 32px rgba(250,204,21,0.10),
            0 6px 20px rgba(56,189,248,0.05);
        margin-bottom: 0.8rem;
        backdrop-filter: blur(10px);
    }

    [data-testid="stExpander"] details {
        background: rgba(255,255,255,0.60) !important;
        border: 1px solid rgba(148,163,184,0.14) !important;
        border-radius: 18px !important;
        overflow: hidden !important;
        box-shadow: 0 12px 28px rgba(148,163,184,0.08) !important;
        backdrop-filter: blur(10px) !important;
    }

    [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, rgba(239,246,255,0.82), rgba(254,249,195,0.56)) !important;
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    div[data-testid="stDataEditor"] {
        background: rgba(248,252,255,0.92) !important;
        border: 1px solid rgba(148,163,184,0.16) !important;
        border-radius: 16px !important;
        padding: 6px !important;
    }

    .stSelectbox label,
    .stSlider label,
    .stRadio label,
    .stMarkdown,
    p, span {
        color: #0f172a !important;
    }

    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stNumberInput > div > div,
    .stTextInput > div > div {
        border-radius: 14px !important;
    }

    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.85) !important;
        border: 1px solid rgba(148,163,184,0.16) !important;
        box-shadow: 0 8px 18px rgba(148,163,184,0.05) !important;
    }

    .stSlider [data-baseweb="slider"] {
        padding-top: 0.3rem !important;
    }

    .popup-overlay {
        position: fixed;
        inset: 0;
        background: rgba(15,23,42,.28);
        backdrop-filter: blur(6px);
        z-index: 99990;
        pointer-events: none;
    }

    .popup-wrap {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 99991;
        width: min(520px, 86vw);
        pointer-events: none;
    }

    .popup-card {
        background: rgba(255,248,248,.97);
        border: 1px solid rgba(239,68,68,.14);
        border-radius: 20px;
        box-shadow: 0 18px 55px rgba(15,23,42,.18);
        padding: 22px 22px 18px 22px;
        font-family: "Segoe UI", sans-serif;
    }

    .popup-title {
        color: #991b1b;
        font-size: 1.85rem;
        font-weight: 900;
        line-height: 1.08;
        margin: 0 38px 10px 0;
        text-transform: uppercase;
    }

    .popup-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 14px;
    }

    .popup-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: .74rem;
        font-weight: 800;
        line-height: 1;
        border: 1px solid transparent;
    }

    .popup-badge.red {
        background: #fee2e2;
        color: #b91c1c;
        border-color: #fecaca;
    }

    .popup-badge.yellow {
        background: #fef3c7;
        color: #a16207;
        border-color: #fde68a;
    }

    .popup-detail {
        color: #3f3f46;
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 14px;
    }

    .popup-note {
        color: #2563eb;
        font-size: .78rem;
        font-weight: 700;
        background: #eff6ff;
        display: inline-block;
        padding: 7px 10px;
        border-radius: 999px;
    }

    div[data-testid="stButton"]:has(> button[kind="secondary"]) {
        position: fixed !important;
        top: calc(50% - 132px) !important;
        left: calc(50% + 210px) !important;
        z-index: 100001 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stButton"]:has(> button[kind="secondary"]) button {
        width: 36px !important;
        min-width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        border: none !important;
        background: #ef4444 !important;
        color: white !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
        box-shadow: 0 10px 22px rgba(239,68,68,.30) !important;
        padding: 0 !important;
        cursor: pointer !important;
    }

    div[data-testid="stButton"]:has(> button[kind="secondary"]) button:hover {
        background: #dc2626 !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================
@st.cache_data
def get_data():
    try:
        df = load_data().copy()

        numeric_cols = [
            "DEGER", "YAS", "CINSIYET", "OKUL_BITEN",
            "SAGLIK_SIGORTA_1", "HBS_KOD5", "GELIR_TOPLAM", "MEDENI_DURUM"
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "GELIR_TOPLAM" in df.columns:
            df.loc[df["GELIR_TOPLAM"] < 0, "GELIR_TOPLAM"] = np.nan
            df["LOG_GELIR_TOPLAM"] = np.where(
                df["GELIR_TOPLAM"].notna(),
                np.log1p(df["GELIR_TOPLAM"]),
                np.nan
            )

        return df

    except Exception as e:
        st.error("Veri yüklenemedi.")
        st.exception(e)
        return pd.DataFrame()

def map_label(value, mapping):
    if pd.isna(value):
        return "Bilinmiyor"
    try:
        return mapping.get(int(value), str(int(value)))
    except Exception:
        return str(value)

def build_single_select_options(series, mapping=None):
    series = series.dropna()
    raw_values = sorted(series.unique().tolist(), key=lambda x: str(x))

    if mapping:
        labels = [map_label(v, mapping) for v in raw_values]
        reverse = {map_label(v, mapping): v for v in raw_values}
    else:
        labels = [str(v) for v in raw_values]
        reverse = {str(v): v for v in raw_values}

    return ["Tümü"] + labels, reverse

def shorten_text(text, limit=28):
    text = str(text)
    return text if len(text) <= limit else text[:limit - 3] + "..."

def safe_mean(df, group_col, value_col):
    clean_df = df[[group_col, value_col]].dropna().copy()
    if clean_df.empty:
        return pd.DataFrame(columns=[group_col, value_col])

    return (
        clean_df.groupby(group_col, dropna=False)[value_col]
        .mean()
        .reset_index()
        .sort_values(value_col, ascending=False)
    )

def style_figure(fig, height, title=None, x_title="", y_title=""):
    layout_dict = dict(
        height=height,
        plot_bgcolor="rgba(255,255,255,0.14)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=55 if title else 15, b=10),
        font=dict(color=TEXT_MID, size=13),
        xaxis_title=x_title,
        yaxis_title=y_title
    )

    if title is not None and str(title).strip() != "" and str(title).lower() != "undefined":
        layout_dict["title"] = title
        layout_dict["title_font_size"] = 18
        layout_dict["title_font_color"] = TEXT_DARK

    fig.update_layout(**layout_dict)

    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        zeroline=False,
        tickfont=dict(color=TEXT_SOFT, size=12),
        title_font=dict(color=TEXT_MID, size=13)
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zeroline=False,
        tickfont=dict(color=TEXT_SOFT, size=12),
        title_font=dict(color=TEXT_MID, size=13)
    )

    return fig

def fmt_number(value, digits=2):
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_int(value):
    if pd.isna(value):
        return "-"
    return f"{int(value):,}".replace(",", ".")

def build_filter_signature(selected_gender, selected_age, selected_edu, selected_ins, selected_medeni, selected_log_gelir):
    return str({
        "gender": selected_gender,
        "age": selected_age,
        "edu": selected_edu,
        "ins": selected_ins,
        "medeni": selected_medeni,
        "gelir": selected_log_gelir
    })

def get_filter_context_text(selected_gender, selected_age, selected_edu, selected_ins, selected_medeni, selected_log_gelir):
    parts = []

    if selected_gender != "Tümü":
        parts.append(f"cinsiyet={selected_gender}")
    if selected_age is not None:
        parts.append(f"yaş aralığı={selected_age[0]}-{selected_age[1]}")
    if selected_edu != "Tümü":
        parts.append(f"eğitim={selected_edu}")
    if selected_ins != "Tümü":
        parts.append(f"sigorta={selected_ins}")
    if selected_medeni != "Tümü":
        parts.append(f"medeni durum={selected_medeni}")
    if selected_log_gelir is not None:
        gelir_alt = int(np.expm1(selected_log_gelir[0]))
        gelir_ust = int(np.expm1(selected_log_gelir[1]))
        parts.append(f"yaklaşık gelir={fmt_int(gelir_alt)}-{fmt_int(gelir_ust)} TL")

    if not parts:
        return "genel görünümde"

    return ", ".join(parts) + " seçimine göre"

def open_data_alert(title, subtitle, detail, risk="Yüksek Risk", tag2="Dar Örneklem", tag3="Filtre Kaynaklı İçgörü"):
    st.session_state.alert_data = {
        "title": str(title),
        "subtitle": str(subtitle),
        "detail": str(detail),
        "risk": str(risk),
        "tag2": str(tag2),
        "tag3": str(tag3)
    }
    st.session_state.alert_open = True

def render_alert():
    if not st.session_state.get("alert_open", False):
        return

    data = st.session_state.alert_data

    safe_title = html.escape(str(data.get("title", "")))
    safe_subtitle = html.escape(str(data.get("subtitle", "")))
    safe_detail = html.escape(str(data.get("detail", ""))).replace("\n", "<br>")
    safe_risk = html.escape(str(data.get("risk", "Yüksek Risk")))
    safe_tag2 = html.escape(str(data.get("tag2", "Dar Örneklem")))
    safe_tag3 = html.escape(str(data.get("tag3", "Filtre Kaynaklı İçgörü")))

    popup_html = (
        '<div class="popup-overlay"></div>'
        '<div class="popup-wrap">'
            '<div class="popup-card">'
                f'<div class="popup-title">{safe_title}: {safe_subtitle}</div>'
                '<div class="popup-badges">'
                    f'<div class="popup-badge red">▲ {safe_risk}</div>'
                    f'<div class="popup-badge yellow">⚠ {safe_tag2}</div>'
                '</div>'
                f'<div class="popup-detail">{safe_detail}</div>'
                f'<div class="popup-note">{safe_tag3}</div>'
            '</div>'
        '</div>'
    )
    st.markdown(popup_html, unsafe_allow_html=True)

    close_clicked = st.button("✕", key="alert_close_btn", type="secondary")
    if close_clicked:
        st.session_state.alert_open = False
        st.rerun()

def generate_filter_change_alert(filtered_df, filter_context):
    if len(filtered_df) < 500:
        return {
            "title": "DİKKAT",
            "subtitle": "FİLTRELENEN VERİ DARALDI",
            "detail": (
                f"Filtreleme seçenekleriniz sonucunda analiz edilen kayıt sayısı "
                f"{fmt_int(len(filtered_df))}'in altına düştü. "
                f"Gösterilen grafikler daha dar bir grubu temsil etmektedir. "
                f"Genelleme yaparken dikkatli olunuz."
            ),
            "risk": "Yüksek Risk",
            "tag2": "Dar Örneklem",
            "tag3": "Filtre Kaynaklı İçgörü"
        }

    if "DEGER" not in filtered_df.columns or not filtered_df["DEGER"].notna().any():
        return None

    deger = pd.to_numeric(filtered_df["DEGER"], errors="coerce").dropna()
    if deger.empty:
        return None

    positive = deger[deger > 0]
    if len(positive) >= 20:
        q1 = positive.quantile(0.25)
        q3 = positive.quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        outlier_ratio = (positive > upper_bound).mean()

        if outlier_ratio >= 0.12:
            return {
                "title": "DİKKAT",
                "subtitle": "UÇ HARCAMA DEĞERLERİ ARTTI",
                "detail": (
                    f"{filter_context} göre olağan dışı yüksek sağlık harcaması oranı "
                    f"%{outlier_ratio * 100:.1f} seviyesine çıktı. "
                    f"Bu seçili grupta maliyet yoğunluğu artmış görünüyor."
                ),
                "risk": "Yüksek Risk",
                "tag2": "Uç Değer Artışı",
                "tag3": "Maliyet Yoğunluğu"
            }

    avg_val = deger.mean()
    med_val = deger.median()
    std_val = deger.std()

    if avg_val > 180:
        return {
            "title": "DİKKAT",
            "subtitle": "ORTALAMA SAĞLIK HARCAMASI YÜKSELDİ",
            "detail": (
                f"{filter_context} ortalama sağlık harcaması {fmt_number(avg_val)} seviyesine çıktı. "
                f"Seçili grubun harcama yükü genel yapıya göre daha yüksek görünüyor."
            ),
            "risk": "Yüksek Risk",
            "tag2": "Ortalama Artışı",
            "tag3": "Maliyet Yoğunluğu"
        }

    if med_val < 10 and avg_val > 100:
        return {
            "title": "DİKKAT",
            "subtitle": "HARCAMA DAĞILIMI DENGESİZLEŞTİ",
            "detail": (
                f"{filter_context} medyan harcama {fmt_number(med_val)}, ortalama ise {fmt_number(avg_val)} oldu. "
                f"Az sayıdaki yüksek harcama genel dağılımı yukarı çekiyor olabilir."
            ),
            "risk": "Yüksek Risk",
            "tag2": "Dengesiz Dağılım",
            "tag3": "Aykırı Etki"
        }

    if std_val > 800:
        return {
            "title": "DİKKAT",
            "subtitle": "HARCAMA OYNAKLIĞI ARTTI",
            "detail": (
                f"{filter_context} harcama değerlerinin standart sapması {fmt_number(std_val)} seviyesine yükseldi. "
                f"Maliyet yapısı homojen görünmüyor."
            ),
            "risk": "Orta Risk",
            "tag2": "Yüksek Oynaklık",
            "tag3": "Dağılım Riski"
        }

    if "HBS_KOD5" in filtered_df.columns:
        temp = filtered_df[["HBS_KOD5", "DEGER"]].dropna().copy()
        if not temp.empty:
            temp["HARCAMA_KALEMI"] = temp["HBS_KOD5"].apply(lambda x: map_label(x, HBS_KOD5_MAP))
            grouped = temp.groupby("HARCAMA_KALEMI")["DEGER"].sum().sort_values(ascending=False)
            if len(grouped) > 0 and grouped.sum() > 0:
                top_label = grouped.index[0]
                share = grouped.iloc[0] / grouped.sum() * 100
                if share >= 45:
                    return {
                        "title": "DİKKAT",
                        "subtitle": "TEK HARCAMA KALEMİNDE YOĞUNLAŞMA VAR",
                        "detail": (
                            f"{filter_context} toplam sağlık harcamasının %{share:.1f}'i '{top_label}' kaleminde toplandı."
                        ),
                        "risk": "Orta Risk",
                        "tag2": "Yoğunlaşma",
                        "tag3": "Kalem Baskısı"
                    }

    if "OKUL_BITEN" in filtered_df.columns:
        edu_df = safe_mean(filtered_df, "OKUL_BITEN", "DEGER")
        if len(edu_df) >= 2:
            edu_df["EGITIM_ETIKET"] = edu_df["OKUL_BITEN"].apply(lambda x: map_label(x, OKUL_BITEN_MAP))
            edu_top = edu_df.iloc[0]["EGITIM_ETIKET"]
            edu_diff = edu_df.iloc[0]["DEGER"] - edu_df.iloc[-1]["DEGER"]
            if edu_diff >= 120:
                return {
                    "title": "DİKKAT",
                    "subtitle": "EĞİTİM GRUPLARI ARASINDA FARK VAR",
                    "detail": (
                        f"{filter_context} eğitim grupları arasında ortalama sağlık harcaması farkı yükseldi. "
                        f"En yüksek grup: '{edu_top}'."
                    ),
                    "risk": "Orta Risk",
                    "tag2": "Eğitim Farkı",
                    "tag3": "Segment Ayrışması"
                }

    if "SAGLIK_SIGORTA_1" in filtered_df.columns:
        ins_df = safe_mean(filtered_df, "SAGLIK_SIGORTA_1", "DEGER")
        if len(ins_df) >= 2:
            ins_df["SIGORTA_ETIKET"] = ins_df["SAGLIK_SIGORTA_1"].apply(lambda x: map_label(x, SAGLIK_SIGORTA_MAP))
            ins_top = ins_df.iloc[0]["SIGORTA_ETIKET"]
            ins_diff = ins_df.iloc[0]["DEGER"] - ins_df.iloc[-1]["DEGER"]
            if ins_diff >= 100:
                return {
                    "title": "DİKKAT",
                    "subtitle": "SİGORTA TÜRÜNE GÖRE HARCAMA FARKI ARTTI",
                    "detail": (
                        f"{filter_context} sigorta türleri arasında belirgin sağlık harcaması farkı oluştu. "
                        f"En yüksek grup: '{ins_top}'."
                    ),
                    "risk": "Orta Risk",
                    "tag2": "Sigorta Farkı",
                    "tag3": "Kırılım Etkisi"
                }

    if "LOG_GELIR_TOPLAM" in filtered_df.columns:
        gelir_df = filtered_df[["LOG_GELIR_TOPLAM", "DEGER"]].dropna()
        if len(gelir_df) >= 30:
            corr_val = gelir_df["LOG_GELIR_TOPLAM"].corr(gelir_df["DEGER"])
            if pd.notna(corr_val):
                if corr_val >= 0.55:
                    return {
                        "title": "DİKKAT",
                        "subtitle": "GELİR VE SAĞLIK HARCAMASI BAĞLANTISI GÜÇLÜ",
                        "detail": (
                            f"{filter_context} gelir ile sağlık harcaması arasında güçlü pozitif ilişki tespit edildi "
                            f"(korelasyon: {corr_val:.2f})."
                        ),
                        "risk": "Orta Risk",
                        "tag2": "Güçlü Korelasyon",
                        "tag3": "Gelir Etkisi"
                    }
                if corr_val <= -0.35:
                    return {
                        "title": "DİKKAT",
                        "subtitle": "GELİR VE HARCAMA ARASINDA TERS YÖNLÜ İLİŞKİ VAR",
                        "detail": (
                            f"{filter_context} gelir ile sağlık harcaması arasında negatif yönlü güçlü ilişki tespit edildi "
                            f"(korelasyon: {corr_val:.2f})."
                        ),
                        "risk": "Orta Risk",
                        "tag2": "Negatif İlişki",
                        "tag3": "Gelir Davranışı"
                    }

    return None

# =========================================================
# VERİ
# =========================================================
df = get_data()
filtered_df = df.copy()
active_filters = 0

selected_gender = "Tümü"
selected_age = None
selected_edu = "Tümü"
selected_ins = "Tümü"
selected_medeni = "Tümü"
selected_log_gelir = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("Filtreler")
    st.caption("Veriyi sosyal, ekonomik ve sağlık profiline göre filtreleyebilirsin.")

    if "CINSIYET" in filtered_df.columns:
        gender_options, gender_reverse = build_single_select_options(filtered_df["CINSIYET"], CINSIYET_MAP)
        selected_gender = st.selectbox("Cinsiyet", gender_options)
        if selected_gender != "Tümü":
            filtered_df = filtered_df[filtered_df["CINSIYET"] == gender_reverse[selected_gender]]
            active_filters += 1

    if "YAS" in filtered_df.columns and filtered_df["YAS"].notna().any():
        min_age = int(filtered_df["YAS"].min())
        max_age = int(filtered_df["YAS"].max())
        selected_age = st.slider("Yaş Aralığı", min_age, max_age, (min_age, max_age))
        filtered_df = filtered_df[
            filtered_df["YAS"].between(selected_age[0], selected_age[1], inclusive="both")
        ]
        if selected_age != (min_age, max_age):
            active_filters += 1

    if "OKUL_BITEN" in filtered_df.columns:
        edu_options, edu_reverse = build_single_select_options(filtered_df["OKUL_BITEN"], OKUL_BITEN_MAP)
        selected_edu = st.selectbox("Eğitim Durumu", edu_options)
        if selected_edu != "Tümü":
            filtered_df = filtered_df[filtered_df["OKUL_BITEN"] == edu_reverse[selected_edu]]
            active_filters += 1

    if "SAGLIK_SIGORTA_1" in filtered_df.columns:
        ins_options, ins_reverse = build_single_select_options(filtered_df["SAGLIK_SIGORTA_1"], SAGLIK_SIGORTA_MAP)
        selected_ins = st.selectbox("Sağlık Sigortası", ins_options)
        if selected_ins != "Tümü":
            filtered_df = filtered_df[filtered_df["SAGLIK_SIGORTA_1"] == ins_reverse[selected_ins]]
            active_filters += 1

    if "MEDENI_DURUM" in filtered_df.columns:
        medeni_options, medeni_reverse = build_single_select_options(filtered_df["MEDENI_DURUM"], MEDENI_DURUM_MAP)
        selected_medeni = st.selectbox("Medeni Durum", medeni_options)
        if selected_medeni != "Tümü":
            filtered_df = filtered_df[filtered_df["MEDENI_DURUM"] == medeni_reverse[selected_medeni]]
            active_filters += 1

    if "LOG_GELIR_TOPLAM" in filtered_df.columns and filtered_df["LOG_GELIR_TOPLAM"].notna().any():
        log_income_min = float(filtered_df["LOG_GELIR_TOPLAM"].min())
        log_income_max = float(filtered_df["LOG_GELIR_TOPLAM"].max())

        log_income_min_r = round(log_income_min, 2)
        log_income_max_r = round(log_income_max, 2)

        selected_log_gelir = st.slider(
            "Gelir Aralığı (Log Ölçek)",
            min_value=log_income_min_r,
            max_value=log_income_max_r,
            value=(log_income_min_r, log_income_max_r)
        )

        if selected_log_gelir != (log_income_min_r, log_income_max_r):
            active_filters += 1

        filtered_df = filtered_df[
            filtered_df["LOG_GELIR_TOPLAM"].between(
                selected_log_gelir[0], selected_log_gelir[1], inclusive="both"
            )
        ]

        gelir_alt = int(np.expm1(selected_log_gelir[0]))
        gelir_ust = int(np.expm1(selected_log_gelir[1]))
        st.caption(f"Yaklaşık gelir aralığı: {fmt_int(gelir_alt)} - {fmt_int(gelir_ust)} TL")

# =========================================================
# FİLTRE DEĞİŞİMİ
# =========================================================
current_filter_signature = build_filter_signature(
    selected_gender,
    selected_age,
    selected_edu,
    selected_ins,
    selected_medeni,
    selected_log_gelir
)

filter_changed = st.session_state.last_filter_signature != current_filter_signature
first_load = st.session_state.last_filter_signature is None

if filter_changed and not first_load:
    st.session_state.alert_open = False

st.session_state.last_filter_signature = current_filter_signature

filter_context = get_filter_context_text(
    selected_gender,
    selected_age,
    selected_edu,
    selected_ins,
    selected_medeni,
    selected_log_gelir
)

if filter_changed and not first_load:
    alert = generate_filter_change_alert(filtered_df, filter_context)
    if alert:
        open_data_alert(
            alert["title"],
            alert["subtitle"],
            alert["detail"],
            alert.get("risk", "Yüksek Risk"),
            alert.get("tag2", "Dar Örneklem"),
            alert.get("tag3", "Filtre Kaynaklı İçgörü")
        )

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero-card">
    <div class="hero-title">TÜİK Sağlık Harcaması Dashboard</div>
    <div class="hero-subtitle">
        Sağlık harcamalarını sosyal ve ekonomik göstergelerle birlikte analiz et.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# UYARI
# =========================================================
render_alert()

# =========================================================
# ÜST BİLGİ
# =========================================================
top1, top2 = st.columns([3, 1])

with top1:
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-label">Filtreler sonrası analiz edilen toplam gözlem</div>
            <div class="mini-value">{fmt_int(len(filtered_df))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with top2:
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-label">Aktif filtre</div>
            <div class="mini-value">{active_filters}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# KPI
# =========================================================
if "DEGER" in filtered_df.columns and filtered_df["DEGER"].notna().any():
    deger = filtered_df["DEGER"].dropna()

    st.markdown('<div class="section-title">İstatistiki Özetler</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    kpis = [
        ("Ortalama Harcama", fmt_number(deger.mean())),
        ("Medyan", fmt_number(deger.median())),
        ("Std. Sapma", fmt_number(deger.std())),
        ("Gözlem Sayısı", fmt_int(deger.count()))
    ]

    for col, (label, value) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# =========================================================
# ANA ANALİZ
# =========================================================
main_left, main_right = st.columns([1.7, 1])

with main_left:
    st.markdown('<div class="section-title">Sağlık Harcama Kırılımı</div>', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([2, 1])

    with ctrl1:
        metric_type = st.radio(
            "Gösterim Türü",
            ["Toplam Harcama", "Ortalama Harcama", "Frekans"],
            horizontal=True
        )

    with ctrl2:
        top_n = st.slider("Top N", 5, 12, 8)

    if "HBS_KOD5" in filtered_df.columns and "DEGER" in filtered_df.columns:
        temp = filtered_df.copy()
        temp["HARCAMA_KALEMI"] = temp["HBS_KOD5"].apply(lambda x: map_label(x, HBS_KOD5_MAP))
        temp = temp.dropna(subset=["HARCAMA_KALEMI"])

        if metric_type == "Toplam Harcama":
            grouped = (
                temp.groupby("HARCAMA_KALEMI", dropna=False)["DEGER"]
                .sum()
                .reset_index()
                .sort_values("DEGER", ascending=False)
                .head(top_n)
            )
            value_col = "DEGER"
            title = "Kalemlere Göre Toplam Harcama"
            color = PRIMARY_GREEN

        elif metric_type == "Ortalama Harcama":
            grouped = (
                temp.groupby("HARCAMA_KALEMI", dropna=False)["DEGER"]
                .mean()
                .reset_index()
                .sort_values("DEGER", ascending=False)
                .head(top_n)
            )
            value_col = "DEGER"
            title = "Kalemlere Göre Ortalama Harcama"
            color = SOFT_BLUE

        else:
            grouped = (
                temp.groupby("HARCAMA_KALEMI", dropna=False)
                .size()
                .reset_index(name="FREKANS")
                .sort_values("FREKANS", ascending=False)
                .head(top_n)
            )
            value_col = "FREKANS"
            title = "Kalemlere Göre Frekans"
            color = SOFT_ORANGE

        if not grouped.empty:
            grouped["KISA"] = grouped["HARCAMA_KALEMI"].apply(shorten_text)

            fig_main = px.bar(
                grouped.sort_values(value_col, ascending=True),
                x=value_col,
                y="KISA",
                orientation="h"
            )
            fig_main = style_figure(fig_main, 470, title=title)
            fig_main.update_traces(marker_color=color, marker_line_width=0)
            fig_main.update_yaxes(showgrid=False)
            fig_main.update_xaxes(showgrid=False)
            st.plotly_chart(fig_main, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Bu filtre kombinasyonunda gösterilecek veri bulunamadı.")

with main_right:
    st.markdown('<div class="section-title">Harcama Yoğunluğu</div>', unsafe_allow_html=True)

    if "DEGER" in filtered_df.columns and filtered_df["DEGER"].notna().any():
        log_df = filtered_df[filtered_df["DEGER"] > 0].copy()
        log_df["LOG_DEGER"] = np.log10(log_df["DEGER"])

        if not log_df.empty:
            fig_hist = px.histogram(log_df, x="LOG_DEGER", nbins=35)
            fig_hist = style_figure(
                fig_hist,
                470,
                title="Logaritmik Harcama Dağılımı",
                x_title="Log10 Harcama"
            )
            fig_hist.update_traces(marker_color=SOFT_YELLOW, marker_line_width=0)
            fig_hist.update_xaxes(showgrid=False)
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Dağılım grafiği için pozitif harcama verisi bulunamadı.")

# =========================================================
# SOSYOEKONOMİK KARŞILAŞTIRMALAR
# =========================================================
st.markdown('<div class="section-title">Sosyoekonomik Karşılaştırmalar</div>', unsafe_allow_html=True)

extra1, extra2 = st.columns(2)

with extra1:
    st.markdown('<div class="panel-title">Eğitim Düzeyine Göre Ortalama Harcama</div>', unsafe_allow_html=True)

    if "OKUL_BITEN" in filtered_df.columns and "DEGER" in filtered_df.columns:
        edu_df = safe_mean(filtered_df, "OKUL_BITEN", "DEGER")

        if not edu_df.empty:
            edu_df["EGITIM_ETIKET"] = edu_df["OKUL_BITEN"].apply(lambda x: map_label(x, OKUL_BITEN_MAP))
            edu_df = edu_df[edu_df["EGITIM_ETIKET"] != "Bilinmiyor"]
            edu_df["EGITIM_KISA"] = edu_df["EGITIM_ETIKET"].apply(lambda x: shorten_text(x, 34))

            fig_edu = px.bar(
                edu_df.sort_values("DEGER", ascending=True),
                x="DEGER",
                y="EGITIM_KISA",
                orientation="h"
            )
            fig_edu = style_figure(fig_edu, 430, x_title="Ortalama Harcama")
            fig_edu.update_traces(marker_color=SOFT_EMERALD, marker_line_width=0)
            fig_edu.update_yaxes(showgrid=False)
            fig_edu.update_xaxes(showgrid=False)
            st.plotly_chart(fig_edu, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Eğitim grafiği için veri bulunamadı.")

with extra2:
    st.markdown('<div class="panel-title">Sigorta Türüne Göre Ortalama Harcama</div>', unsafe_allow_html=True)

    if "SAGLIK_SIGORTA_1" in filtered_df.columns and "DEGER" in filtered_df.columns:
        ins_df = safe_mean(filtered_df, "SAGLIK_SIGORTA_1", "DEGER")

        if not ins_df.empty:
            ins_df["SIGORTA_ETIKET"] = ins_df["SAGLIK_SIGORTA_1"].apply(lambda x: map_label(x, SAGLIK_SIGORTA_MAP))
            ins_df = ins_df[ins_df["SIGORTA_ETIKET"] != "Bilinmiyor"]
            ins_df["SIGORTA_KISA"] = ins_df["SIGORTA_ETIKET"].apply(lambda x: shorten_text(x, 34))

            fig_ins = px.bar(
                ins_df.sort_values("DEGER", ascending=True),
                x="DEGER",
                y="SIGORTA_KISA",
                orientation="h"
            )
            fig_ins = style_figure(fig_ins, 430, x_title="Ortalama Harcama")
            fig_ins.update_traces(marker_color=SOFT_ORANGE, marker_line_width=0)
            fig_ins.update_yaxes(showgrid=False)
            fig_ins.update_xaxes(showgrid=False)
            st.plotly_chart(fig_ins, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Sigorta grafiği için veri bulunamadı.")

# =========================================================
# EKONOMİK VE SOSYAL KIRILIM
# =========================================================
st.markdown('<div class="section-title">Ekonomik ve Sosyal Kırılım</div>', unsafe_allow_html=True)

extra3, extra4 = st.columns(2)

with extra3:
    st.markdown('<div class="panel-title">Medeni Duruma Göre Ortalama Harcama</div>', unsafe_allow_html=True)

    if "MEDENI_DURUM" in filtered_df.columns and "DEGER" in filtered_df.columns:
        medeni_df = safe_mean(filtered_df, "MEDENI_DURUM", "DEGER")

        if not medeni_df.empty:
            medeni_df["MEDENI_ETIKET"] = medeni_df["MEDENI_DURUM"].apply(lambda x: map_label(x, MEDENI_DURUM_MAP))
            medeni_df = medeni_df[medeni_df["MEDENI_ETIKET"] != "Bilinmiyor"]

            fig_medeni = px.bar(
                medeni_df.sort_values("DEGER", ascending=True),
                x="DEGER",
                y="MEDENI_ETIKET",
                orientation="h"
            )
            fig_medeni = style_figure(fig_medeni, 430, x_title="Ortalama Harcama")
            fig_medeni.update_traces(marker_color=SOFT_INDIGO, marker_line_width=0)
            fig_medeni.update_yaxes(showgrid=False)
            fig_medeni.update_xaxes(showgrid=False)
            st.plotly_chart(fig_medeni, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Medeni durum grafiği için veri bulunamadı.")
    else:
        st.info("MEDENI_DURUM kolonu bulunamadı.")

with extra4:
    st.markdown('<div class="panel-title">Gelir Seviyesi ile Sağlık Harcaması Arasındaki İlişki</div>', unsafe_allow_html=True)

    if "LOG_GELIR_TOPLAM" in filtered_df.columns and "DEGER" in filtered_df.columns:
        gelir_df = filtered_df[["LOG_GELIR_TOPLAM", "DEGER"]].dropna()

        if not gelir_df.empty:
            upper_x = gelir_df["LOG_GELIR_TOPLAM"].quantile(0.99)
            upper_y = gelir_df["DEGER"].quantile(0.99)

            gelir_df = gelir_df[
                (gelir_df["LOG_GELIR_TOPLAM"] <= upper_x) &
                (gelir_df["DEGER"] <= upper_y)
            ]

            sample_df = gelir_df.sample(min(len(gelir_df), 4000), random_state=42)

            fig_income = px.scatter(
                sample_df,
                x="LOG_GELIR_TOPLAM",
                y="DEGER",
                opacity=0.32
            )
            fig_income = style_figure(
                fig_income,
                430,
                x_title="Log Toplam Gelir",
                y_title="Harcama"
            )
            fig_income.update_traces(
                marker=dict(color=SOFT_CYAN, size=7, line=dict(width=0))
            )
            fig_income.update_xaxes(showgrid=False)
            fig_income.update_yaxes(showgrid=False)
            st.plotly_chart(fig_income, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Gelir-harcama grafiği için veri bulunamadı.")
    else:
        st.info("GELIR_TOPLAM verisi bulunamadı.")

# =========================================================
# İÇGÖRÜ
# =========================================================
st.markdown('<div class="section-title">Öne Çıkan Bulgular</div>', unsafe_allow_html=True)

insight_text = "Bu filtre kombinasyonunda yorum üretmek için yeterli veri bulunamadı."

if "DEGER" in filtered_df.columns and "HBS_KOD5" in filtered_df.columns and filtered_df["DEGER"].notna().any():
    temp_insight = filtered_df.copy()
    temp_insight["HARCAMA_KALEMI"] = temp_insight["HBS_KOD5"].apply(lambda x: map_label(x, HBS_KOD5_MAP))
    top_category = (
        temp_insight.groupby("HARCAMA_KALEMI")["DEGER"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(top_category) > 0:
        top_name = top_category.index[0]
        top_value = top_category.iloc[0]
        overall_mean = filtered_df["DEGER"].mean()

        insight_text = (
            f"En yüksek toplam harcama, <b>{top_name}</b> kaleminde gözlemlendi.<br>"
            f"Toplam harcama: <b>{fmt_number(top_value)}</b><br>"
            f"Genel ortalama harcama: <b>{fmt_number(overall_mean)}</b>"
        )

st.markdown(
    f"""
    <div class="insight-card">
        {insight_text}
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TABLO
# =========================================================
with st.expander("Filtrelenmiş Veri Önizlemesi"):
    preview = filtered_df.copy()

    rename_map = {
        "BIRIMNO": "Birim No",
        "ELDEEDIS_SEKIL": "Elde Ediliş Şekli",
        "HBS_KOD5": "Harcama Kalemi",
        "DEGER": "Tutar",
        "FERTNO": "Fert No",
        "CINSIYET": "Cinsiyet",
        "YAS": "Yaş",
        "YAKINLIK": "Yakınlık",
        "SAGLIK_SIGORTA_1": "Sağlık Sigortası",
        "SAKATLIK_GUNLUK": "Sakatlık Günlük",
        "SAKATLIK_CALISMA": "Sakatlık Çalışma",
        "OKUL_BITEN": "Eğitim",
        "MEDENI_DURUM": "Medeni Durum",
        "GELIR_TOPLAM": "Toplam Gelir",
        "LOG_GELIR_TOPLAM": "Log Toplam Gelir"
    }

    if "CINSIYET" in preview.columns:
        preview["CINSIYET"] = preview["CINSIYET"].apply(lambda x: map_label(x, CINSIYET_MAP))
    if "OKUL_BITEN" in preview.columns:
        preview["OKUL_BITEN"] = preview["OKUL_BITEN"].apply(lambda x: map_label(x, OKUL_BITEN_MAP))
    if "SAGLIK_SIGORTA_1" in preview.columns:
        preview["SAGLIK_SIGORTA_1"] = preview["SAGLIK_SIGORTA_1"].apply(lambda x: map_label(x, SAGLIK_SIGORTA_MAP))
    if "HBS_KOD5" in preview.columns:
        preview["HBS_KOD5"] = preview["HBS_KOD5"].apply(lambda x: map_label(x, HBS_KOD5_MAP))
    if "MEDENI_DURUM" in preview.columns:
        preview["MEDENI_DURUM"] = preview["MEDENI_DURUM"].apply(lambda x: map_label(x, MEDENI_DURUM_MAP))

    if "DEGER" in preview.columns:
        preview["DEGER"] = preview["DEGER"].round(2)
    if "GELIR_TOPLAM" in preview.columns:
        preview["GELIR_TOPLAM"] = preview["GELIR_TOPLAM"].round(2)
    if "LOG_GELIR_TOPLAM" in preview.columns:
        preview["LOG_GELIR_TOPLAM"] = preview["LOG_GELIR_TOPLAM"].round(2)

    existing_rename_map = {k: v for k, v in rename_map.items() if k in preview.columns}
    preview = preview.rename(columns=existing_rename_map)

    preferred_cols = [
        "Birim No",
        "Harcama Kalemi",
        "Tutar",
        "Cinsiyet",
        "Yaş",
        "Yakınlık",
        "Sağlık Sigortası",
        "Eğitim",
        "Medeni Durum",
        "Toplam Gelir",
        "Log Toplam Gelir"
    ]

    available_cols = [col for col in preferred_cols if col in preview.columns]
    if available_cols:
        preview = preview[available_cols]

    st.data_editor(
        preview.head(100),
        use_container_width=True,
        height=380,
        disabled=True,
        hide_index=True
    )