import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard IPH BPS Kab. Jombang", page_icon="📊", layout="wide")

# --- KUSTOMISASI TEMA & WARNA KONTRAS ---
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: rgba(245, 130, 32, 0.1); 
        border-top: 4px solid #F58220; 
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #00A3E0; 
        color: white;
        border: none;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #F58220; 
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# KONFIGURASI DATABASE GOOGLE SHEETS
# ==========================================
# Masukkan tautan Export Google Sheets Anda di dalam tanda kutip di bawah ini.
# Anda bisa menambahkan koma jika memiliki lebih dari satu tautan (misal sheet 2025 dan 2026 terpisah).
GOOGLE_SHEETS_URLS = [
    "https://docs.google.com/spreadsheets/d/1r9-A9_QL6jWRlq6KQcri1pQJtDGoc53JYjZJvpff6ZA/export?format=xlsx",
    "https://docs.google.com/spreadsheets/d/1C_k5IDhvxKU3mD8NbYGw6bWFixpBAKD4gcRxFwgGBsk/export?format=xlsx"
]

# --- FUNGSI MEMUAT DATA DARI CLOUD ---
# Menggunakan cache (ttl=600) artinya aplikasi akan menyegarkan data otomatis setiap 10 menit
@st.cache_data(ttl=600, show_spinner="Mengambil data terbaru dari server Google...")
def load_all_data_from_gsheets():
    list_ringkasan = []
    list_top5 = []
    
    for url in GOOGLE_SHEETS_URLS:
        try:
            response = requests.get(url)
            response.raise_for_status() # Cek apakah link valid
            
            with pd.ExcelFile(BytesIO(response.content), engine='openpyxl') as xls:
                # 1. Load Ringkasan
                sheet_ringkasan = [s for s in xls.sheet_names if "ringkasan" in s.lower()]
                if sheet_ringkasan:
                    df_r = pd.read_excel(xls, sheet_name=sheet_ringkasan[0], skiprows=2)
                    if 'Bulan - Minggu' in df_r.columns:
                        df_r = df_r.dropna(subset=['Bulan - Minggu'])
                        list_ringkasan.append(df_r)
                
                # 2. Load Top 5
                sheet_top5 = [s for s in xls.sheet_names if "top 5" in s.lower() or "top5" in s.lower() or "andil" in s.lower()]
                if sheet_top5:
                    df_t_raw = pd.read_excel(xls, sheet_name=sheet_top5[0], header=None)
                    current_week = None
                    for index, row in df_t_raw.iterrows():
                        val_asli = str(row[0]).strip()
                        val_upper = val_asli.upper() 
                        
                        is_judul_minggu = ("-" in val_upper) and \
                                          ("M1" in val_upper or "M2" in val_upper or "M3" in val_upper or "M4" in val_upper or "M5" in val_upper) and \
                                          ("KOMODITAS" not in val_upper)
                        
                        if is_judul_minggu:
                            current_week = val_asli
                        elif current_week and val_asli.isdigit():
                            list_top5.append({
                                "Minggu": current_week,
                                "Peringkat": int(val_asli),
                                "Komoditas": row[1],
                                "Bobot (wi)": row[2],
                                "Pertumbuhan Harga (%)": row[3],
                                "Andil thd IPH (%)": row[4],
                                "Keterangan": row[5]
                            })
        except Exception as e:
            st.error(f"Gagal menghubungkan ke Google Sheets. Pastikan tautan sudah diset 'Siapa saja bisa melihat' dan ujungnya '/export?format=xlsx'. Error: {e}")
            
    df_ringkasan_final = pd.concat(list_ringkasan, ignore_index=True) if list_ringkasan else pd.DataFrame()
    df_top5_final = pd.DataFrame(list_top5) if list_top5 else pd.DataFrame()
    
    return df_ringkasan_final, df_top5_final

# --- BAGIAN HEADER & LOGO ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    # Karena aplikasi akan di-deploy, pastikan folder 'assets' ada di repositori GitHub
    logo_path = "assets/logo_bps.png"
    import os
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    else:
        st.info("Logo BPS")

with col_title:
    st.markdown("""
        <div style="line-height: 1.1;">
            <h1 style="color: #F58220; margin: 0; padding: 0; font-size: 2.8rem; font-weight: bold;">EWANGI</h1>
            <h3 style="color: #FFFFFF; margin: 5px 0 0 0; padding: 0;">Dashboard Early Warning IPH</h3>
            <h5 style="color: #00A3E0; margin: 5px 0 0 0; padding: 0;">Badan Pusat Statistik Kabupaten Jombang</h5>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR: STATUS DATABASE ---
st.sidebar.markdown('### 📂 Status Database')
st.sidebar.success("✅ Terhubung ke Google Sheets")
st.sidebar.info("Dashboard diperbarui secara otomatis. Admin hanya perlu mengubah angka di Google Sheets.")

if st.sidebar.button("🔄 Tarik Data Sekarang", use_container_width=True):
    st.cache_data.clear() # Membersihkan cache agar mengambil data GSheets paling baru
    st.rerun()

# --- MEMUAT DATA ---
df_ringkasan, df_top5 = load_all_data_from_gsheets()

# Ekstrak Tahun
if not df_ringkasan.empty:
    df_ringkasan['Tahun'] = df_ringkasan['Bulan - Minggu'].astype(str).str.extract(r'(\d{4})')
if not df_top5.empty:
    df_top5['Tahun'] = df_top5['Minggu'].astype(str).str.extract(r'(\d{4})')

# --- TAMPILAN UTAMA (MENGGUNAKAN TABS) ---
if not df_ringkasan.empty and not df_top5.empty:
    
    valid_mask = pd.to_numeric(df_ringkasan['Growth IPH (%)'], errors='coerce').notna()
    df_valid_ringkasan = df_ringkasan[valid_mask]
    
    if not df_valid_ringkasan.empty:
        latest_data = df_valid_ringkasan.iloc[-1]
    else:
        latest_data = df_ringkasan.iloc[-1]
        
    minggu_terakhir = latest_data.get('Bulan - Minggu', '-')
    rentang_tanggal = latest_data.get('Rentang Tanggal', '-')
    growth_terakhir = latest_data.get('Growth IPH (%)', 0)
    arah = latest_data.get('Arah', '-')
    
    st.markdown("### Ringkasan Periode Terkini")
    col1, col2, col3 = st.columns(3)
    col1.metric("Periode Terakhir Terdata", f"{minggu_terakhir}", f"{rentang_tanggal}", delta_color="off")
    try:
        growth_val = float(growth_terakhir)
        col2.metric("Growth IPH Terkini", f"{growth_val:.2f}%", f"{growth_val:.2f}%" if arah=="Naik" else f"{growth_val:.2f}%", delta_color="inverse")
    except:
        col2.metric("Growth IPH Terkini", str(growth_terakhir))
    col3.metric("Status Tren", str(arah))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📈 Ringkasan & Tren IPH", "🔥 Top 5 Andil Komoditas"])
    
    # TAB 1: GRAFIK & TABEL
    with tab1:
        list_tahun = sorted(df_ringkasan['Tahun'].dropna().unique().tolist(), reverse=True)
        opsi_tahun_tab1 = ["Semua"] + list_tahun
        selected_tahun_tab1 = st.selectbox("🗓️ Pilih Periode Data:", opsi_tahun_tab1, key="filter_tab1")
        
        if selected_tahun_tab1 == "Semua":
            df_ringkasan_filtered = df_ringkasan.copy()
        else:
            df_ringkasan_filtered = df_ringkasan[df_ringkasan['Tahun'] == selected_tahun_tab1].copy()

        st.markdown("#### Tren Historis Growth IPH")
        df_ringkasan_filtered['Growth IPH (%)'] = pd.to_numeric(df_ringkasan_filtered['Growth IPH (%)'], errors='coerce')
        
        fig = px.line(df_ringkasan_filtered, x='Bulan - Minggu', y='Growth IPH (%)', markers=True, 
                      hover_data=['Rentang Tanggal', 'Arah'])
        
        fig.update_traces(line=dict(color='#F58220', width=3), marker=dict(size=8, color='#022B69'), connectgaps=True)
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.8)
        # PERBAIKAN: Kembali ke sistem otomatis yang lebih rapi
        fig.update_layout(
            xaxis_title="", 
            yaxis_title="Growth IPH (%)", 
            margin=dict(t=10, b=20),
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                type='category',     # Menjaga agar garis tetap rapi dan tidak menebak tanggal
                tickmode='auto',     # Sistem otomatis mengatur kerapatan label
                tickangle=-90        # (Opsional) Memaksa teks miring 90 derajat ke atas agar lebih banyak label yang bisa muat
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### Tabel Data Ringkasan")
        df_ringkasan_tabel = df_ringkasan_filtered[['Bulan - Minggu', 'Rentang Tanggal', 'Growth IPH (%)', 'Arah']].copy()
        df_ringkasan_tabel = df_ringkasan_tabel.iloc[::-1]
        
        def color_arah(val):
            if str(val) == 'Naik':
                return 'color: #ff4b4b; font-weight: bold;'
            elif str(val) == 'Turun':
                return 'color: #09ab3b; font-weight: bold;'
            return ''
        
        def format_growth(val):
            try:
                return f"{float(val):.3f}%"
            except:
                return val
        
        df_ringkasan_tabel['Growth IPH (%)'] = df_ringkasan_tabel['Growth IPH (%)'].apply(format_growth)
        st.dataframe(df_ringkasan_tabel.style.map(color_arah, subset=['Arah']), use_container_width=True, hide_index=True)

    # TAB 2: TOP 5 ANDIL
    with tab2:
        st.markdown("#### Tabel Top 5 Komoditas Penyumbang Andil per Minggu")
        list_tahun_top5 = sorted(df_top5['Tahun'].dropna().unique().tolist(), reverse=True)
        
        if len(list_tahun_top5) > 0:
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                selected_tahun_tab2 = st.selectbox("1️⃣ Pilih Tahun:", list_tahun_top5, key="filter_tab2_tahun")
                
            df_top5_year = df_top5[df_top5['Tahun'] == selected_tahun_tab2]
            list_minggu = df_top5_year['Minggu'].unique()
            
            with col_filter2:
                selected_minggu = st.selectbox("2️⃣ Pilih Periode Minggu:", reversed(list_minggu), key="filter_tab2_minggu")
                
            filtered_top5 = df_top5_year[df_top5_year['Minggu'] == selected_minggu].drop(columns=['Minggu', 'Tahun'])
            
            def style_keterangan_andil(row):
                if 'KENAIKAN' in str(row['Keterangan']):
                    return ['color: #ff4b4b; font-weight: bold;'] * len(row)
                elif 'PENURUNAN' in str(row['Keterangan']):
                    return ['color: #09ab3b; font-weight: bold;'] * len(row)
                return [''] * len(row)

            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(filtered_top5.style.apply(style_keterangan_andil, axis=1), use_container_width=True, hide_index=True)
            
else:
    st.warning("Belum ada data yang berhasil ditarik dari Google Sheets. Periksa kembali tautan Anda.")