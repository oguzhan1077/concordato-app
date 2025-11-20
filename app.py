import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from datetime import datetime, timedelta

# Sayfa Ayarları
st.set_page_config(
    page_title="İlan Analiz Paneli",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Veritabanı Bağlantısı
@st.cache_resource
def get_db_connection():
    """Veritabanı bağlantısını oluşturur ve önbelleğe alır."""
    if DB_PASSWORD:
        db_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    else:
        db_url = f"mysql+mysqlconnector://{DB_USER}@{DB_HOST}/{DB_NAME}"
    
    engine = create_engine(db_url)
    return engine

# Veri Çekme
@st.cache_data(ttl=300)  # 5 dakikada bir önbelleği temizle
def load_data():
    """Veritabanından verileri çeker."""
    engine = get_db_connection()
    try:
        # İlanlar ve Borçluları birleştirerek çekelim
        # Şimdilik sadece ilanlar tablosunu temel alalım, detaylar gerekirse join yaparız
        query = """
        SELECT 
            i.id, i.ilan_no, i.baslik, i.sehir, i.ilce, i.kurum, i.ilan_turu, 
            i.eklenme_tarihi, i.link,
            b.borclu_adi, b.borclu_tipi, b.karar_turu
        FROM ilanlar i
        LEFT JOIN ilan_borclulari b ON i.id = b.ilan_id
        ORDER BY i.eklenme_tarihi DESC
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

# --- Arayüz ---

st.title("📊 Konkordato ve İflas İlanları Analiz Paneli")
st.markdown("Veritabanındaki ilanları filtreleyebilir, grafiklerle analiz edebilirsiniz.")

# Veriyi Yükle
with st.spinner('Veriler yükleniyor...'):
    df = load_data()

if df.empty:
    st.warning("Veritabanında henüz veri yok veya bağlantı kurulamadı.")
    st.stop()

# --- Sidebar Filtreleri ---
st.sidebar.header("Filtreler")

# Tarih Filtresi
min_date = df['eklenme_tarihi'].min().date() if not df.empty else datetime.now().date()
max_date = df['eklenme_tarihi'].max().date() if not df.empty else datetime.now().date()

baslangic_tarihi = st.sidebar.date_input(
    "Başlangıç Tarihi", 
    min_date,
    min_value=min_date,
    max_value=max_date
)
bitis_tarihi = st.sidebar.date_input(
    "Bitiş Tarihi", 
    max_date,
    min_value=min_date,
    max_value=max_date
)

# Şehir Filtresi
sehirler = ['Tümü'] + sorted(list(df['sehir'].dropna().unique()))
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", sehirler)

# İlan Türü Filtresi
ilan_turleri = ['Tümü'] + sorted(list(df['ilan_turu'].dropna().unique()))
secilen_tur = st.sidebar.selectbox("İlan Türü", ilan_turleri)

# Kelime Arama
arama_metni = st.sidebar.text_input("İlan veya Borçlu Ara", "")

# --- Veriyi Filtrele ---
filtered_df = df.copy()

# Tarih filtresi
if baslangic_tarihi and bitis_tarihi:
    # Pandas datetime karşılaştırması için dönüşüm
    filtered_df['eklenme_tarihi'] = pd.to_datetime(filtered_df['eklenme_tarihi'])
    filtered_df = filtered_df[
        (filtered_df['eklenme_tarihi'].dt.date >= baslangic_tarihi) & 
        (filtered_df['eklenme_tarihi'].dt.date <= bitis_tarihi)
    ]

# Şehir filtresi
if secilen_sehir != 'Tümü':
    filtered_df = filtered_df[filtered_df['sehir'] == secilen_sehir]

# Tür filtresi
if secilen_tur != 'Tümü':
    filtered_df = filtered_df[filtered_df['ilan_turu'] == secilen_tur]

# Arama filtresi
if arama_metni:
    arama_metni = arama_metni.lower()
    filtered_df = filtered_df[
        filtered_df['baslik'].str.lower().str.contains(arama_metni, na=False) |
        filtered_df['borclu_adi'].str.lower().str.contains(arama_metni, na=False) |
        filtered_df['ilan_no'].str.lower().str.contains(arama_metni, na=False)
    ]

# --- Özet Kartlar ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Toplam İlan", len(filtered_df))

with col2:
    unique_borclu = filtered_df['borclu_adi'].nunique()
    st.metric("Borçlu Sayısı", unique_borclu)

with col3:
    en_cok_sehir = filtered_df['sehir'].mode()[0] if not filtered_df.empty else "-"
    st.metric("En Yoğun Şehir", en_cok_sehir)

with col4:
    son_tarih = filtered_df['eklenme_tarihi'].max()
    tarih_str = son_tarih.strftime("%d.%m.%Y") if not pd.isnull(son_tarih) else "-"
    st.metric("Son Veri Tarihi", tarih_str)

st.divider()

# --- Grafikler ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Günlük İlan Sayısı")
    if not filtered_df.empty:
        daily_counts = filtered_df.groupby(filtered_df['eklenme_tarihi'].dt.date).size().reset_index(name='count')
        fig_line = px.line(daily_counts, x='eklenme_tarihi', y='count', markers=True)
        fig_line.update_layout(xaxis_title="Tarih", yaxis_title="İlan Sayısı")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Gösterilecek veri yok.")

with col_right:
    st.subheader("İlan Türü Dağılımı")
    if not filtered_df.empty:
        tur_counts = filtered_df['ilan_turu'].value_counts().reset_index(name='count')
        fig_pie = px.pie(tur_counts, values='count', names='ilan_turu', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Gösterilecek veri yok.")

# Şehirlere Göre Dağılım (Eğer birden fazla şehir varsa)
if len(filtered_df['sehir'].unique()) > 1:
    st.subheader("Şehirlere Göre Dağılım")
    city_counts = filtered_df['sehir'].value_counts().head(10).reset_index(name='count')
    fig_bar = px.bar(city_counts, x='sehir', y='count', color='count')
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Detaylı Tablo ---
st.subheader("Detaylı İlan Listesi")
st.dataframe(
    filtered_df[['eklenme_tarihi', 'ilan_no', 'baslik', 'sehir', 'ilan_turu', 'borclu_adi', 'karar_turu']],
    use_container_width=True,
    hide_index=True
)

# İndirme Butonu
st.download_button(
    label="Verileri Excel Olarak İndir",
    data=filtered_df.to_csv(index=False).encode('utf-8-sig'),
    file_name='ilan_listesi.csv',
    mime='text/csv',
)

