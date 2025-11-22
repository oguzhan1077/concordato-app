import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from datetime import datetime
import re
from io import BytesIO
from models import Base # Tabloları oluşturmak için

# Sayfa Ayarları
st.set_page_config(
    page_title="Konkordato İlanları Takip",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State
if 'selected_ilan_id' not in st.session_state:
    st.session_state.selected_ilan_id = None
if 'show_detail' not in st.session_state:
    st.session_state.show_detail = False

# Veritabanı Bağlantısı
@st.cache_resource
def get_db_connection():
    if DB_PASSWORD:
        db_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    else:
        db_url = f"mysql+mysqlconnector://{DB_USER}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(db_url)
    
    # Tabloların varlığını kontrol et ve oluştur
    Base.metadata.create_all(engine)
    
    return engine

# Veri Çekme
@st.cache_data(ttl=300)
def load_data():
    engine = get_db_connection()
    try:
        query = """
        SELECT 
            i.id, i.ilan_no, i.baslik, i.sehir, i.ilce, i.kurum, i.ilan_turu, 
            i.yayin_tarihi, i.metin, i.link,
            b.id as borclu_id, b.borclu_adi, b.borclu_tipi, b.tc_vkn, 
            b.ticaret_sicil_no, b.adres, b.karar_turu, b.karar_ozeti,
            b.karar_tarihi, b.karar_baslangic_tarihi, b.muhlet_suresi,
            b.mahkeme_adi, b.dosya_esas_no, b.komiserler, b.durusma_tarihi
        FROM ilanlar i
        LEFT JOIN ilan_borclulari b ON i.id = b.ilan_id
        ORDER BY i.yayin_tarihi DESC, i.id DESC
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

# Tarih parse fonksiyonu
def parse_tarih(tarih_str):
    if pd.isna(tarih_str) or not tarih_str: return None
    try: return pd.to_datetime(tarih_str, format='%d.%m.%Y', dayfirst=True)
    except: pass
    try: return pd.to_datetime(tarih_str, format='%Y-%m-%d')
    except: pass
    try: return pd.to_datetime(tarih_str, dayfirst=True)
    except: return None

# --- CSS ---
st.markdown("""
<style>
    .metric-card {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #FAFAFA;
    }
    .metric-label {
        font-size: 12px;
        color: #AAAAAA;
    }
    .stDataFrame { font-size: 12px; }
    /* İlan Listesi Başlığı ile Filtreler arası boşluğu ayarla */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stMarkdownContainer"] p:contains("İlan Listesi")) {
        margin-bottom: -1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 📋 Konkordato İlanları Takip")
    st.markdown("---")
    if st.button("🏠 Ana Sayfa", use_container_width=True):
        st.session_state.show_detail = False
        st.session_state.selected_ilan_id = None
        st.rerun()
    st.markdown("---")
    st.markdown("### 🔐 Üyelik")
    st.info("Üyelik özelliği yakında aktif olacak.")

# --- Detay Sayfası ---
if st.session_state.show_detail and st.session_state.selected_ilan_id:
    engine = get_db_connection()
    query = """
    SELECT 
        i.id, i.ilan_no, i.baslik, i.sehir, i.ilce, i.kurum, i.ilan_turu, 
        i.yayin_tarihi, i.metin, i.link,
        b.id as borclu_id, b.borclu_adi, b.borclu_tipi, b.tc_vkn, 
        b.ticaret_sicil_no, b.adres, b.karar_turu, b.karar_ozeti,
        b.karar_tarihi, b.karar_baslangic_tarihi, b.muhlet_suresi,
        b.mahkeme_adi, b.dosya_esas_no, b.komiserler, b.durusma_tarihi
    FROM ilanlar i
    LEFT JOIN ilan_borclulari b ON i.id = b.ilan_id
    WHERE i.id = %s
    """
    detail_df = pd.read_sql(query, engine, params=(st.session_state.selected_ilan_id,))
    
    if not detail_df.empty:
        secilen_ilan = detail_df.iloc[0]
        if st.button("← Geri Dön"):
            st.session_state.show_detail = False
            st.session_state.selected_ilan_id = None
            st.rerun()
        
        st.subheader(f"📄 İlan Detayları: {secilen_ilan['ilan_no']}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**İlan Bilgileri**")
            st.write(f"**İlan No:** {secilen_ilan['ilan_no']}")
            st.write(f"**Başlık:** {secilen_ilan['baslik']}")
            st.write(f"**Yayın Tarihi:** {secilen_ilan['yayin_tarihi']}")
            st.write(f"**Şehir:** {secilen_ilan['sehir']}")
            st.write(f"**İlçe:** {secilen_ilan['ilce']}")
            st.write(f"**İlan Türü:** {secilen_ilan['ilan_turu']}")
            st.write(f"**Kurum:** {secilen_ilan['kurum']}")
            if pd.notna(secilen_ilan['link']):
                st.markdown(f"**Link:** [İlanı Görüntüle]({secilen_ilan['link']})")
        with col2:
            st.markdown("**İlan Metni**")
            if pd.notna(secilen_ilan['metin']):
                st.text_area("İlan Metni", secilen_ilan['metin'], height=200, disabled=True, label_visibility="collapsed")
            else:
                st.info("Metin bulunamadı.")
        
        borclular = detail_df[detail_df['borclu_id'].notna()]
        if not borclular.empty:
            st.divider()
            st.subheader("👤 Borçlu Detayları")
            for idx, borclu in borclular.iterrows():
                if pd.notna(borclu['borclu_adi']):
                    with st.expander(f"🔹 {borclu['borclu_adi']}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Kişisel Bilgiler**")
                            st.write(f"**Adı:** {borclu['borclu_adi']}")
                            st.write(f"**Tipi:** {borclu['borclu_tipi']}")
                            if pd.notna(borclu['tc_vkn']): st.write(f"**TC/VKN:** {borclu['tc_vkn']}")
                            if pd.notna(borclu['ticaret_sicil_no']): st.write(f"**Ticaret Sicil No:** {borclu['ticaret_sicil_no']}")
                            if pd.notna(borclu['adres']): st.write(f"**Adres:** {borclu['adres']}")
                        with col2:
                            st.markdown("**Karar Bilgileri**")
                            if pd.notna(borclu['karar_turu']): st.write(f"**Karar Türü:** {borclu['karar_turu']}")
                            if pd.notna(borclu['karar_tarihi']): st.write(f"**Karar Tarihi:** {borclu['karar_tarihi']}")
                            if pd.notna(borclu['karar_baslangic_tarihi']): st.write(f"**Başlangıç Tarihi:** {borclu['karar_baslangic_tarihi']}")
                            if pd.notna(borclu['muhlet_suresi']): st.write(f"**Mühlet Süresi:** {borclu['muhlet_suresi']}")
                            if pd.notna(borclu['mahkeme_adi']): st.write(f"**Mahkeme:** {borclu['mahkeme_adi']}")
                            if pd.notna(borclu['dosya_esas_no']): st.write(f"**Dosya Esas No:** {borclu['dosya_esas_no']}")
                            if pd.notna(borclu['komiserler']): st.write(f"**Komiserler:** {borclu['komiserler']}")
                            if pd.notna(borclu['durusma_tarihi']): st.write(f"**Duruşma Tarihi:** {borclu['durusma_tarihi']}")
                        if pd.notna(borclu['karar_ozeti']) and str(borclu['karar_ozeti']).strip():
                            st.markdown("---")
                            st.markdown("### 📝 Karar Özeti")
                            st.info(borclu['karar_ozeti'])
        else:
            st.info("Bu ilan için henüz borçlu analizi yapılmamış.")
    st.stop()

# --- Ana Sayfa ---
st.markdown("### 📊 Konkordato ve İflas İlanları")

with st.spinner('Veriler yükleniyor...'):
    df = load_data()

if df.empty:
    st.warning("Veritabanında henüz veri yok veya bağlantı kurulamadı.")
    st.stop()

df['yayin_tarihi_parsed'] = df['yayin_tarihi'].apply(parse_tarih)

# Filtre State
tarihli_df = df[df['yayin_tarihi_parsed'].notna()]
if not tarihli_df.empty:
    min_date, max_date = tarihli_df['yayin_tarihi_parsed'].min().date(), tarihli_df['yayin_tarihi_parsed'].max().date()
else:
    min_date, max_date = datetime.now().date(), datetime.now().date()

if 'baslangic_tarihi' not in st.session_state: st.session_state.baslangic_tarihi = min_date
if 'bitis_tarihi' not in st.session_state: st.session_state.bitis_tarihi = max_date
if 'secilen_sehir' not in st.session_state: st.session_state.secilen_sehir = 'Tümü'
if 'arama_metni' not in st.session_state: st.session_state.arama_metni = ''

# --- Minimal Özet Kartlar (HTML) ---
col1, col2, col3 = st.columns(3)
unique_all = df.drop_duplicates(subset=['id'])
en_cok_sehir = unique_all['sehir'].mode()[0] if not unique_all.empty and not unique_all['sehir'].mode().empty else "-"
son_tarih = df['yayin_tarihi_parsed'].max()
son_tarih_str = son_tarih.strftime("%d.%m.%Y") if not pd.isnull(son_tarih) else "-"

with col1:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Toplam İlan</div><div class="metric-value">{len(unique_all)}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">En Yoğun Şehir</div><div class="metric-value">{en_cok_sehir}</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Son Yayın Tarihi</div><div class="metric-value">{son_tarih_str}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- İlan Listesi & Filtreler ---
st.subheader("📋 İlan Listesi")

# Filtreler (Başlığın Hemen Altında)
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 2, 2.5, 1])

with c1:
    bs = st.date_input("Başlangıç", st.session_state.baslangic_tarihi, min_value=min_date, max_value=max_date, label_visibility="collapsed")
with c2:
    bt = st.date_input("Bitiş", st.session_state.bitis_tarihi, min_value=min_date, max_value=max_date, label_visibility="collapsed")
with c3:
    sehirler = ['Tümü'] + sorted([s for s in df['sehir'].dropna().unique() if s])
    s_sehir = st.selectbox("Şehir", sehirler, index=sehirler.index(st.session_state.secilen_sehir) if st.session_state.secilen_sehir in sehirler else 0, label_visibility="collapsed")
with c4:
    s_arama = st.text_input("Ara", st.session_state.arama_metni, placeholder="İlan, borçlu veya şehir ara...", label_visibility="collapsed")
with c5:
    st.markdown("<br>", unsafe_allow_html=True)  # Dikey hizalama için
    if st.button("🔄 Sıfırla", use_container_width=True):
        st.session_state.baslangic_tarihi = min_date
        st.session_state.bitis_tarihi = max_date
        st.session_state.secilen_sehir = 'Tümü'
        st.session_state.arama_metni = ''
        st.rerun()

# State update
if bs != st.session_state.baslangic_tarihi: st.session_state.baslangic_tarihi = bs
if bt != st.session_state.bitis_tarihi: st.session_state.bitis_tarihi = bt
if s_sehir != st.session_state.secilen_sehir: st.session_state.secilen_sehir = s_sehir
if s_arama != st.session_state.arama_metni: st.session_state.arama_metni = s_arama

# Filtreleme İşlemi
filtered_df = df.copy()
if st.session_state.baslangic_tarihi and st.session_state.bitis_tarihi:
    filtered_df = filtered_df[
        (filtered_df['yayin_tarihi_parsed'].notna()) &
        (filtered_df['yayin_tarihi_parsed'].dt.date >= st.session_state.baslangic_tarihi) & 
        (filtered_df['yayin_tarihi_parsed'].dt.date <= st.session_state.bitis_tarihi)
    ]
if st.session_state.secilen_sehir != 'Tümü':
    filtered_df = filtered_df[filtered_df['sehir'] == st.session_state.secilen_sehir]
if st.session_state.arama_metni:
    arama_lower = st.session_state.arama_metni.lower()
    filtered_df = filtered_df[
        filtered_df['baslik'].str.lower().str.contains(arama_lower, na=False) |
        filtered_df['borclu_adi'].str.lower().str.contains(arama_lower, na=False) |
        filtered_df['ilan_no'].str.lower().str.contains(arama_lower, na=False)
    ]

# --- Tablo ---
st.markdown("---")

unique_ilanlar = filtered_df.drop_duplicates(subset=['id'])
if unique_ilanlar.empty:
    st.info("Filtrelere uygun ilan bulunamadı.")
else:
    liste_df = unique_ilanlar.copy()
    
    # İlana ait tüm borçluları bul ve birleştir
    ilan_borclu_map = df.groupby('id')['borclu_adi'].apply(lambda x: ", ".join([str(i) for i in x.dropna().unique() if i])).to_dict()
    liste_df['davalı_adi'] = liste_df['id'].map(ilan_borclu_map)
    
    # Görüntüleme için DF
    display_df = liste_df[['id', 'yayin_tarihi', 'ilan_no', 'baslik', 'sehir', 'davalı_adi']].copy()
    
    display_df = display_df.rename(columns={
        'yayin_tarihi': 'Yayın Tarihi',
        'ilan_no': 'İlan No',
        'baslik': 'Başlık',
        'sehir': 'Şehir',
        'davalı_adi': 'Davalı Adı'
    })

    # Streamlit Dataframe selection API kullanımı
    event = st.dataframe(
        display_df.drop(columns=['id']),
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )
    
    # Seçim kontrolü
    if len(event.selection['rows']) > 0:
        selected_index = event.selection['rows'][0]
        selected_id = display_df.iloc[selected_index]['id']
        st.session_state.selected_ilan_id = int(selected_id)
        st.session_state.show_detail = True
        st.rerun()

# İndirme
if not unique_ilanlar.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CSV İndirme
    csv = display_df.drop(columns=['id']).to_csv(index=False).encode('utf-8-sig')
    
    # XLSX İndirme - Detaylı bilgilerle
    # Her borçlu için ayrı satır oluştur
    excel_data = []
    for _, ilan in unique_ilanlar.iterrows():
        ilan_id = ilan['id']
        # Bu ilana ait tüm borçluları bul
        borclular = filtered_df[filtered_df['id'] == ilan_id]
        
        if borclular.empty or borclular['borclu_id'].isna().all():
            # Borçlu yoksa sadece ilan bilgileri
            excel_data.append({
                'Yayın Tarihi': ilan['yayin_tarihi'],
                'İlan No': ilan['ilan_no'],
                'Başlık': ilan['baslik'],
                'Şehir': ilan['sehir'],
                'İlçe': ilan['ilce'],
                'Kurum': ilan['kurum'],
                'İlan Türü': ilan['ilan_turu'],
                'Borçlu Adı': '',
                'Borçlu Tipi': '',
                'TC/VKN': '',
                'Ticaret Sicil No': '',
                'Adres': '',
                'Karar Türü': '',
                'Karar Tarihi': '',
                'Başlangıç Tarihi': '',
                'Mühlet Süresi': '',
                'Mahkeme': '',
                'Dosya Esas No': '',
                'Komiserler': '',
                'Duruşma Tarihi': '',
                'Karar Özeti': ''
            })
        else:
            # Her borçlu için ayrı satır
            for _, borclu in borclular.iterrows():
                if pd.notna(borclu['borclu_id']):
                    excel_data.append({
                        'Yayın Tarihi': ilan['yayin_tarihi'],
                        'İlan No': ilan['ilan_no'],
                        'Başlık': ilan['baslik'],
                        'Şehir': ilan['sehir'],
                        'İlçe': ilan['ilce'],
                        'Kurum': ilan['kurum'],
                        'İlan Türü': ilan['ilan_turu'],
                        'Borçlu Adı': borclu['borclu_adi'],
                        'Borçlu Tipi': borclu['borclu_tipi'],
                        'TC/VKN': borclu['tc_vkn'],
                        'Ticaret Sicil No': borclu['ticaret_sicil_no'],
                        'Adres': borclu['adres'],
                        'Karar Türü': borclu['karar_turu'],
                        'Karar Tarihi': borclu['karar_tarihi'],
                        'Başlangıç Tarihi': borclu['karar_baslangic_tarihi'],
                        'Mühlet Süresi': borclu['muhlet_suresi'],
                        'Mahkeme': borclu['mahkeme_adi'],
                        'Dosya Esas No': borclu['dosya_esas_no'],
                        'Komiserler': borclu['komiserler'],
                        'Duruşma Tarihi': borclu['durusma_tarihi'],
                        'Karar Özeti': borclu['karar_ozeti']
                    })
    
    excel_df = pd.DataFrame(excel_data)
    
    # Excel dosyasını BytesIO'ya yaz
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        excel_df.to_excel(writer, index=False, sheet_name='İlanlar ve Borçlular')
    excel_bytes = output.getvalue()
    
    # İndirme butonları
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 CSV İndir", csv, f'ilanlar_{datetime.now().strftime("%Y%m%d")}.csv', "text/csv", use_container_width=True)
    with col2:
        st.download_button("📊 XLSX İndir (Detaylı)", excel_bytes, f'ilanlar_detayli_{datetime.now().strftime("%Y%m%d")}.xlsx', "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# --- Analiz Grafikleri ---
if not unique_ilanlar.empty:
    st.markdown("---")
    st.subheader("📊 Analiz Grafikleri")
    
    # Benzersiz ilanları kullan (aynı ilan birden fazla sayılmasın)
    unique_for_graph = unique_ilanlar.copy()
    
    # Günlük İlan Sayısı
    daily_counts = unique_for_graph.groupby(unique_for_graph['yayin_tarihi_parsed'].dt.date).size().reset_index(name='count')
    daily_counts = daily_counts.sort_values('yayin_tarihi_parsed')
    
    fig_line = px.line(daily_counts, x='yayin_tarihi_parsed', y='count', 
                       title='Günlük İlan Sayısı',
                       labels={'yayin_tarihi_parsed': 'Tarih', 'count': 'Adet'})
    
    # X ekseni tarih formatını sadece gün yap
    fig_line.update_xaxes(tickformat="%d.%m.%Y")
    fig_line.update_layout(height=350)
    
    st.plotly_chart(fig_line, use_container_width=True)

    # Şehir Dağılımı (En çok 15 şehir) - Benzersiz ilanları kullan
    if len(unique_for_graph['sehir'].unique()) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        city_counts = unique_for_graph['sehir'].value_counts().head(15).reset_index(name='count')
        fig_bar = px.bar(city_counts, x='sehir', y='count', color='count',
                         title='En Çok İlan Çıkan Şehirler',
                         labels={'sehir': 'Şehir', 'count': 'İlan Sayısı'})
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
