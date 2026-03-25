import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.express as px

# ENV yükle
load_dotenv()

# MySQL bağlantı
engine = create_engine(
    f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
)

# Sayfa ayarı
st.set_page_config(page_title="TÜİK Dashboard", layout="wide")

st.title("📊 TÜİK Veri Dashboard")

# Veri çek
@st.cache_data
def load_data():
    query = f"SELECT * FROM {os.getenv('MYSQL_TABLE')} LIMIT 100000"
    return pd.read_sql(query, engine)

df = load_data()

st.success(f"Toplam veri: {df.shape[0]} satır")

# Sidebar filtreler
st.sidebar.header("Filtreler")

if "CINSIYET" in df.columns:
    cinsiyet = st.sidebar.multiselect("Cinsiyet", df["CINSIYET"].unique())
    if cinsiyet:
        df = df[df["CINSIYET"].isin(cinsiyet)]

if "YAS" in df.columns:
    yas = st.sidebar.slider("Yaş", int(df["YAS"].min()), int(df["YAS"].max()), (18, 60))
    df = df[(df["YAS"] >= yas[0]) & (df["YAS"] <= yas[1])]

# KPI
col1, col2, col3 = st.columns(3)

col1.metric("Toplam Kayıt", df.shape[0])
if "YAS" in df.columns:
    col2.metric("Ortalama Yaş", round(df["YAS"].mean(), 1))
if "DEGER" in df.columns:
    col3.metric("Toplam Değer", round(df["DEGER"].sum(), 2))

# Grafikler
st.subheader("📈 Analizler")

if "CINSIYET" in df.columns:
    fig1 = px.histogram(df, x="CINSIYET", title="Cinsiyet Dağılımı")
    st.plotly_chart(fig1, use_container_width=True)

if "YAS" in df.columns:
    fig2 = px.histogram(df, x="YAS", title="Yaş Dağılımı")
    st.plotly_chart(fig2, use_container_width=True)

if "OKUL_BITEN" in df.columns:
    fig3 = px.histogram(df, x="OKUL_BITEN", title="Eğitim Durumu")
    st.plotly_chart(fig3, use_container_width=True)

# Tablo
st.subheader("📋 Veri Önizleme")
st.dataframe(df.head(100))