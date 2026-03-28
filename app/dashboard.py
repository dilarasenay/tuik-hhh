import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db.db import load_data

st.set_page_config(
    page_title="TÜİK Sağlık Harcaması Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(168, 85, 247, 0.16), transparent 22%),
            radial-gradient(circle at top right, rgba(34, 211, 238, 0.14), transparent 24%),
            radial-gradient(circle at bottom left, rgba(236, 72, 153, 0.12), transparent 22%),
            linear-gradient(135deg, #070b17 0%, #0b1224 45%, #081120 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1520px;
        padding-top: 1.1rem;
        padding-bottom: 2rem;
        padding-left: 1.8rem;
        padding-right: 1.8rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10,16,32,0.94) 0%, rgba(11,18,36,0.96) 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    .hero-card {
        background:
            linear-gradient(135deg, rgba(139, 92, 246, 0.90) 0%, rgba(236, 72, 153, 0.84) 50%, rgba(34, 211, 238, 0.78) 100%);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 28px;
        padding: 32px 34px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.04),
            0 0 34px rgba(168, 85, 247, 0.25),
            0 0 44px rgba(34, 211, 238, 0.10);
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.08;
        margin-bottom: 0.4rem;
        text-shadow: 0 0 14px rgba(255,255,255,0.10);
    }

    .hero-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.92);
        max-width: 980px;
        line-height: 1.6;
    }

    .mini-card {
        background: linear-gradient(135deg, rgba(12, 26, 54, 0.80), rgba(16, 38, 74, 0.60));
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 0 18px rgba(34, 211, 238, 0.08);
        min-height: 82px;
    }

    .mini-label {
        font-size: 0.88rem;
        color: #cbd5e1;
        margin-bottom: 0.35rem;
    }

    .mini-value {
        font-size: 1.8rem;
        font-weight: 900;
        color: #ffffff;
    }

    .section-title {
        font-size: 1.22rem;
        font-weight: 850;
        color: #f8fafc;
        margin-top: 0.1rem;
        margin-bottom: 0.8rem;
        text-shadow: 0 0 12px rgba(34,211,238,0.10);
    }

    .kpi-card {
        background: linear-gradient(135deg, rgba(13, 20, 38, 0.92), rgba(17, 26, 48, 0.78));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 18px 20px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.03),
            0 0 20px rgba(139, 92, 246, 0.10);
        min-height: 110px;
    }

    .kpi-label {
        font-size: 0.92rem;
        color: #cbd5e1;
        margin-bottom: 0.45rem;
    }

    .kpi-value {
        font-size: 1.95rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.05;
        text-shadow: 0 0 8px rgba(236,72,153,0.08);
    }

    .panel-card {
        background: linear-gradient(135deg, rgba(8, 14, 29, 0.94), rgba(12, 20, 38, 0.84));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 24px;
        padding: 16px 16px 8px 16px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.03),
            0 0 24px rgba(34, 211, 238, 0.06);
        margin-bottom: 1rem;
    }

    .insight-card {
        background: linear-gradient(135deg, rgba(236,72,153,0.12), rgba(139,92,246,0.10), rgba(34,211,238,0.08));
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 5px solid #22d3ee;
        border-radius: 20px;
        padding: 16px 18px;
        color: #f8fafc;
        line-height: 1.65;
        box-shadow: 0 0 22px rgba(236,72,153,0.08);
    }

    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 1rem;
    }

    .sidebar-note {
        font-size: 0.9rem;
        color: #cbd5e1;
        margin-top: -0.2rem;
        margin-bottom: 1rem;
    }

    div[data-baseweb="select"] > div {
        background: rgba(11, 18, 36, 0.88) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        color: white !important;
    }

    .stSlider [data-baseweb="slider"] {
        padding-top: 0.35rem;
    }

    .stCheckbox label, .stRadio label {
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================
@st.cache_data
def get_data():
    df = load_data().copy()
    numeric_cols = ["DEGER", "YAS", "CINSIYET", "OKUL_BITEN", "SAGLIK_SIGORTA_1", "HBS_KOD5"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def map_label(value, mapping):
    if pd.isna(value):
        return "Bilinmiyor"
    try:
        return mapping.get(int(value), str(int(value)))
    except Exception:
        return str(value)

def build_single_select_options(series, mapping):
    raw_values = sorted(series.dropna().unique().tolist())
    labels = [map_label(v, mapping) for v in raw_values]
    reverse = {map_label(v, mapping): v for v in raw_values}
    return ["Tümü"] + labels, reverse

def shorten_text(text, limit=28):
    text = str(text)
    return text if len(text) <= limit else text[:limit - 3] + "..."

def safe_mean(df, group_col, value_col):
    return (
        df.groupby(group_col, dropna=False)[value_col]
        .mean()
        .reset_index()
        .sort_values(value_col, ascending=False)
    )

# =========================================================
# VERİ
# =========================================================
df = get_data()
filtered_df = df.copy()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown('<div class="sidebar-title">Filtreler</div>', unsafe_allow_html=True)
st.sidebar.markdown(
    '<div class="sidebar-note">Kategori seçimlerini sade tuttum; böylece görünüm daha temiz ve premium kalıyor.</div>',
    unsafe_allow_html=True
)

active_filters = 0

if "CINSIYET" in filtered_df.columns:
    gender_options, gender_reverse = build_single_select_options(filtered_df["CINSIYET"], CINSIYET_MAP)
    selected_gender = st.sidebar.selectbox("Cinsiyet", gender_options)
    if selected_gender != "Tümü":
        filtered_df = filtered_df[filtered_df["CINSIYET"] == gender_reverse[selected_gender]]
        active_filters += 1

if "YAS" in filtered_df.columns and filtered_df["YAS"].notna().any():
    min_age = int(filtered_df["YAS"].min())
    max_age = int(filtered_df["YAS"].max())
    selected_age = st.sidebar.slider("Yaş Aralığı", min_age, max_age, (min_age, max_age))
    filtered_df = filtered_df[
        (filtered_df["YAS"] >= selected_age[0]) &
        (filtered_df["YAS"] <= selected_age[1])
    ]
    if selected_age != (min_age, max_age):
        active_filters += 1

if "OKUL_BITEN" in filtered_df.columns:
    edu_options, edu_reverse = build_single_select_options(filtered_df["OKUL_BITEN"], OKUL_BITEN_MAP)
    selected_edu = st.sidebar.selectbox("Eğitim Durumu", edu_options)
    if selected_edu != "Tümü":
        filtered_df = filtered_df[filtered_df["OKUL_BITEN"] == edu_reverse[selected_edu]]
        active_filters += 1

if "SAGLIK_SIGORTA_1" in filtered_df.columns:
    ins_options, ins_reverse = build_single_select_options(filtered_df["SAGLIK_SIGORTA_1"], SAGLIK_SIGORTA_MAP)
    selected_ins = st.sidebar.selectbox("Sağlık Sigortası", ins_options)
    if selected_ins != "Tümü":
        filtered_df = filtered_df[filtered_df["SAGLIK_SIGORTA_1"] == ins_reverse[selected_ins]]
        active_filters += 1

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero-card">
    <div class="hero-title">TÜİK Sağlık Harcaması Dashboard</div>
    <div class="hero-subtitle">
        Sağlık harcama kalemleri ile demografik değişkenler arasındaki ilişkiyi etkileşimli filtreler,
        istatistiki özetler ve karşılaştırmalı görselleştirmeler üzerinden inceleyen neon temalı analitik panel.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# ÜST BİLGİ
# =========================================================
top1, top2 = st.columns([3, 1])

with top1:
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-label">Filtreler sonrası analiz edilen toplam gözlem</div>
            <div class="mini-value">{len(filtered_df):,}</div>
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
        ("Ortalama Harcama", f"{deger.mean():,.2f}"),
        ("Medyan", f"{deger.median():,.2f}"),
        ("Std. Sapma", f"{deger.std():,.2f}"),
        ("Gözlem Sayısı", f"{deger.count():,}")
    ]

    for col, (label, value) in zip([c1, c2, c3, c4], kpis):
        col.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# ANA PANEL
# =========================================================
main_left, main_right = st.columns([1.7, 1])

with main_left:
    st.markdown('<div class="section-title">Sağlık Harcama Kalemi Analizi</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([2, 1])
    with ctrl1:
        metric_type = st.radio(
            "Gösterim Türü",
            ["Toplam Harcama", "Ortalama Harcama", "Frekans"],
            horizontal=True
        )
    with ctrl2:
        top_n = st.slider("Top N", 5, 12, 8)

    if "HBS_KOD5" in filtered_df.columns:
        temp = filtered_df.copy()
        temp["HARCAMA_KALEMI"] = temp["HBS_KOD5"].apply(lambda x: map_label(x, HBS_KOD5_MAP))

        if metric_type == "Toplam Harcama":
            grouped = (
                temp.groupby("HARCAMA_KALEMI", dropna=False)["DEGER"]
                .sum()
                .reset_index()
                .sort_values("DEGER", ascending=False)
                .head(top_n)
            )
            value_col = "DEGER"
            title = "Sağlık Harcama Kalemlerine Göre Toplam Harcama"
            color = "#22d3ee"

        elif metric_type == "Ortalama Harcama":
            grouped = (
                temp.groupby("HARCAMA_KALEMI", dropna=False)["DEGER"]
                .mean()
                .reset_index()
                .sort_values("DEGER", ascending=False)
                .head(top_n)
            )
            value_col = "DEGER"
            title = "Sağlık Harcama Kalemlerine Göre Ortalama Harcama"
            color = "#a855f7"

        else:
            grouped = (
                temp.groupby("HARCAMA_KALEMI", dropna=False)
                .size()
                .reset_index(name="FREKANS")
                .sort_values("FREKANS", ascending=False)
                .head(top_n)
            )
            value_col = "FREKANS"
            title = "Sağlık Harcama Kalemlerine Göre Frekans"
            color = "#fb7185"

        grouped["KISA"] = grouped["HARCAMA_KALEMI"].apply(shorten_text)

        fig_main = px.bar(
            grouped.sort_values(value_col, ascending=True),
            x=value_col,
            y="KISA",
            orientation="h",
            title=title
        )
        fig_main.update_layout(
            height=470,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=60, b=10),
            title_font_size=18,
            title_font_color="#f8fafc",
            font=dict(color="#e2e8f0"),
            xaxis_title="",
            yaxis_title=""
        )
        fig_main.update_traces(marker_color=color)
        fig_main.update_xaxes(gridcolor="rgba(255,255,255,0.10)")
        fig_main.update_yaxes(showgrid=False)
        st.plotly_chart(fig_main, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with main_right:
    st.markdown('<div class="section-title">Dağılım Özeti</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    if "DEGER" in filtered_df.columns and filtered_df["DEGER"].notna().any():
        fig_hist = px.histogram(
            filtered_df,
            x="DEGER",
            nbins=35,
            title="Sağlık Harcaması Dağılımı"
        )
        fig_hist.update_layout(
            height=470,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=60, b=10),
            title_font_size=18,
            title_font_color="#f8fafc",
            font=dict(color="#e2e8f0"),
            xaxis_title="Harcama Değeri",
            yaxis_title=""
        )
        fig_hist.update_traces(marker_color="#f472b6")
        fig_hist.update_xaxes(showgrid=False)
        fig_hist.update_yaxes(gridcolor="rgba(255,255,255,0.10)")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ALT GRAFİKLER
# =========================================================
bottom1, bottom2 = st.columns(2)

with bottom1:
    st.markdown('<div class="section-title">Yaşa Göre Ortalama Harcama</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    if "YAS" in filtered_df.columns and "DEGER" in filtered_df.columns:
        age_df = (
            filtered_df.groupby("YAS", dropna=False)["DEGER"]
            .mean()
            .reset_index()
            .sort_values("YAS")
        )
        fig_age = px.line(age_df, x="YAS", y="DEGER", title="Yaş Eğilimi")
        fig_age.update_layout(
            height=390,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=60, b=10),
            title_font_size=18,
            title_font_color="#f8fafc",
            font=dict(color="#e2e8f0"),
            xaxis_title="Yaş",
            yaxis_title=""
        )
        fig_age.update_traces(line=dict(color="#a855f7", width=3))
        fig_age.update_xaxes(showgrid=False)
        fig_age.update_yaxes(gridcolor="rgba(255,255,255,0.10)")
        st.plotly_chart(fig_age, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with bottom2:
    st.markdown('<div class="section-title">Cinsiyete Göre Ortalama Harcama</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    if "CINSIYET" in filtered_df.columns and "DEGER" in filtered_df.columns:
        gender_df = safe_mean(filtered_df, "CINSIYET", "DEGER")
        gender_df["CINSIYET_ETIKET"] = gender_df["CINSIYET"].apply(lambda x: map_label(x, CINSIYET_MAP))

        fig_gender = px.bar(
            gender_df,
            x="CINSIYET_ETIKET",
            y="DEGER",
            title="Cinsiyet Karşılaştırması"
        )
        fig_gender.update_layout(
            height=390,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=60, b=10),
            title_font_size=18,
            title_font_color="#f8fafc",
            font=dict(color="#e2e8f0"),
            xaxis_title="",
            yaxis_title=""
        )
        fig_gender.update_traces(marker_color="#8b5cf6")
        fig_gender.update_xaxes(showgrid=False)
        fig_gender.update_yaxes(gridcolor="rgba(255,255,255,0.10)")
        st.plotly_chart(fig_gender, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# EĞİTİM / SİGORTA
# =========================================================
extra1, extra2 = st.columns(2)

with extra1:
    st.markdown('<div class="section-title">Eğitim Durumuna Göre Ortalama Harcama</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    if "OKUL_BITEN" in filtered_df.columns and "DEGER" in filtered_df.columns:
        edu_df = safe_mean(filtered_df, "OKUL_BITEN", "DEGER")
        edu_df["EGITIM_ETIKET"] = edu_df["OKUL_BITEN"].apply(lambda x: map_label(x, OKUL_BITEN_MAP))
        edu_df["EGITIM_KISA"] = edu_df["EGITIM_ETIKET"].apply(lambda x: shorten_text(x, 32))

        fig_edu = px.bar(
            edu_df.sort_values("DEGER", ascending=True),
            x="DEGER",
            y="EGITIM_KISA",
            orientation="h",
            title="Eğitim Kırılımı"
        )
        fig_edu.update_layout(
            height=430,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=60, b=10),
            title_font_size=18,
            title_font_color="#f8fafc",
            font=dict(color="#e2e8f0"),
            xaxis_title="",
            yaxis_title=""
        )
        fig_edu.update_traces(marker_color="#fb7185")
        fig_edu.update_xaxes(gridcolor="rgba(255,255,255,0.10)")
        fig_edu.update_yaxes(showgrid=False)
        st.plotly_chart(fig_edu, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with extra2:
    st.markdown('<div class="section-title">Sigorta Türüne Göre Ortalama Harcama</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    if "SAGLIK_SIGORTA_1" in filtered_df.columns and "DEGER" in filtered_df.columns:
        ins_df = safe_mean(filtered_df, "SAGLIK_SIGORTA_1", "DEGER")
        ins_df["SIGORTA_ETIKET"] = ins_df["SAGLIK_SIGORTA_1"].apply(lambda x: map_label(x, SAGLIK_SIGORTA_MAP))
        ins_df["SIGORTA_KISA"] = ins_df["SIGORTA_ETIKET"].apply(lambda x: shorten_text(x, 32))

        fig_ins = px.bar(
            ins_df.sort_values("DEGER", ascending=True),
            x="DEGER",
            y="SIGORTA_KISA",
            orientation="h",
            title="Sigorta Kırılımı"
        )
        fig_ins.update_layout(
            height=430,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=60, b=10),
            title_font_size=18,
            title_font_color="#f8fafc",
            font=dict(color="#e2e8f0"),
            xaxis_title="",
            yaxis_title=""
        )
        fig_ins.update_traces(marker_color="#38bdf8")
        fig_ins.update_xaxes(gridcolor="rgba(255,255,255,0.10)")
        fig_ins.update_yaxes(showgrid=False)
        st.plotly_chart(fig_ins, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# İÇGÖRÜ
# =========================================================
st.markdown('<div class="section-title">Öne Çıkan İçgörü</div>', unsafe_allow_html=True)

insight_text = "Yeterli veri bulunamadı."

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
            f"Filtrelenen veri setinde en yüksek toplam harcama <b>{top_name}</b> kaleminde görülmektedir. "
            f"Bu kalemde toplam harcama <b>{top_value:,.2f}</b> düzeyindedir. "
            f"Genel ortalama sağlık harcaması ise <b>{overall_mean:,.2f}</b> olarak hesaplanmıştır."
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
show_table = st.checkbox("Filtrelenmiş veri önizlemesini göster")

if show_table:
    preview = filtered_df.copy()

    if "CINSIYET" in preview.columns:
        preview["CINSIYET"] = preview["CINSIYET"].apply(lambda x: map_label(x, CINSIYET_MAP))
    if "OKUL_BITEN" in preview.columns:
        preview["OKUL_BITEN"] = preview["OKUL_BITEN"].apply(lambda x: map_label(x, OKUL_BITEN_MAP))
    if "SAGLIK_SIGORTA_1" in preview.columns:
        preview["SAGLIK_SIGORTA_1"] = preview["SAGLIK_SIGORTA_1"].apply(lambda x: map_label(x, SAGLIK_SIGORTA_MAP))
    if "HBS_KOD5" in preview.columns:
        preview["HBS_KOD5"] = preview["HBS_KOD5"].apply(lambda x: map_label(x, HBS_KOD5_MAP))

    st.markdown('<div class="section-title">Filtrelenmiş Veri Önizleme</div>', unsafe_allow_html=True)
    st.dataframe(preview.head(100), use_container_width=True)