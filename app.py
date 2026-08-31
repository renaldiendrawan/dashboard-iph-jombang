import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob

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

# --- KONFIGURASI DIREKTORI ARSIP ---
DATA_DIR = "data_arsip"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- FUNGSI UNTUK MENGGABUNGKAN SELURUH DATA DARI ARSIP ---
def load_all_data():
    all_files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))
    
    list_ringkasan = []
    list_top5 = []
    
    for file in all_files:
        try:
            xls = pd.ExcelFile(file, engine='openpyxl')
            
            # 1. Load Ringkasan
            sheet_ringkasan = [s for s in xls.sheet_names if "ringkasan" in s.lower()]
            if sheet_ringkasan:
                df_r = pd.read_excel(file, sheet_name=sheet_ringkasan[0], skiprows=2, engine='openpyxl')
                if 'Bulan - Minggu' in df_r.columns:
                    df_r = df_r.dropna(subset=['Bulan - Minggu'])
                    list_ringkasan.append(df_r)
                else:
                    st.sidebar.error(f"Kolom 'Bulan - Minggu' tidak ditemukan di {file}.")
            
            # 2. Load Top 5
            sheet_top5 = [s for s in xls.sheet_names if "top 5" in s.lower()]
            if sheet_top5:
                df_t_raw = pd.read_excel(file, sheet_name=sheet_top5[0], header=None, engine='openpyxl')
                current_week = None
                for index, row in df_t_raw.iterrows():
                    val = str(row[0]).strip()
                    if "MINGGU" in val and "s/d" in val:
                        current_week = val
                    elif current_week and val.isdigit():
                        list_top5.append({
                            "Minggu": current_week,
                            "Peringkat": int(val),
                            "Komoditas": row[1],
                            "Bobot (wi)": row[2],
                            "Pertumbuhan Harga (%)": row[3],
                            "Andil thd IPH (%)": row[4],
                            "Keterangan": row[5]
                        })
        except Exception as e:
            # Mengabaikan pesan Permission Denied karena wajar jika file sedang dibuka user
            if "Permission denied" not in str(e):
                st.sidebar.error(f"Error pada file {os.path.basename(file)}: {e}")
            
    df_ringkasan_final = pd.concat(list_ringkasan, ignore_index=True) if list_ringkasan else pd.DataFrame()
    df_top5_final = pd.DataFrame(list_top5) if list_top5 else pd.DataFrame()
    
    return df_ringkasan_final, df_top5_final

# --- BAGIAN HEADER & LOGO ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    logo_path = os.path.join("assets", "logo_bps.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    else:
        st.info("Logo BPS")

with col_title:
    # Menggunakan HTML tag agar jarak spasi antar judul (margin/padding) rapat dan rapi
    st.markdown("""
        <div style="line-height: 1.1;">
            <h1 style="color: #F58220; margin: 0; padding: 0; font-size: 2.8rem; font-weight: bold;">EWANGI</h1>
            <h3 style="color: #FFFFFF; margin: 5px 0 0 0; padding: 0;">Dashboard Early Warning IPH</h3>
            <h5 style="color: #00A3E0; margin: 5px 0 0 0; padding: 0;">Badan Pusat Statistik Kabupaten Jombang</h5>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR: SISTEM UPLOAD & ARSIP ---
st.sidebar.markdown('### 📂 Kelola Data (Arsip)')
st.sidebar.info("Pastikan file tidak sedang dibuka di Excel saat diunggah.")
uploaded_file = st.sidebar.file_uploader("Tambah File Excel Baru (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"File '{uploaded_file.name}' berhasil ditambahkan ke arsip!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**File Tersimpan di Server:**")
for f_name in os.listdir(DATA_DIR):
    if f_name.endswith(".xlsx"):
        st.sidebar.caption(f"📄 {f_name}")

# --- MEMUAT DATA ---
df_ringkasan, df_top5 = load_all_data()

# --- TAMPILAN UTAMA (MENGGUNAKAN TABS) ---
if not df_ringkasan.empty and not df_top5.empty:
    
    # Menyiapkan data metrik terbaru
    latest_data = df_ringkasan.iloc[-1]
    minggu_terakhir = latest_data.get('Bulan - Minggu', '-')
    rentang_tanggal = latest_data.get('Rentang Tanggal', '-')
    growth_terakhir = latest_data.get('Growth IPH (%)', 0)
    arah = latest_data.get('Arah', '-')
    
    st.markdown("#### Ringkasan Periode Terkini")
    col1, col2, col3 = st.columns(3)
    col1.metric("Periode Terakhir Terdata", f"{minggu_terakhir}", f"{rentang_tanggal}", delta_color="off")
    try:
        growth_val = float(growth_terakhir)
        col2.metric("Growth IPH Terkini", f"{growth_val:.2f}%", f"{growth_val:.2f}%" if arah=="Naik" else f"{growth_val:.2f}%", delta_color="inverse")
    except:
        col2.metric("Growth IPH Terkini", str(growth_terakhir))
    col3.metric("Status Tren", str(arah))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # MEMBUAT TABS
    tab1, tab2 = st.tabs(["📈 Ringkasan & Tren IPH", "🔥 Top 5 Andil Komoditas"])
    
    # ==========================================
    # TAB 1: GRAFIK TREN & TABEL RINGKASAN
    # ==========================================
    with tab1:
        # 1. Menampilkan Grafik Lebar Penuh
        st.markdown("#### Tren Historis Growth IPH")
        df_ringkasan['Growth IPH (%)'] = pd.to_numeric(df_ringkasan['Growth IPH (%)'], errors='coerce')
        fig = px.line(df_ringkasan, x='Bulan - Minggu', y='Growth IPH (%)', markers=True, 
                      hover_data=['Rentang Tanggal', 'Arah'])
        
        # MENYAMBUNGKAN GARIS YANG PUTUS (CONNECT GAPS)
        fig.update_traces(
            line=dict(color='#F58220', width=3), 
            marker=dict(size=8, color='#022B69'),
            connectgaps=True  # Baris ajaib untuk menyambungkan titik yang hilang
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.8)
        fig.update_layout(xaxis_title="", yaxis_title="Growth IPH (%)", margin=dict(t=10, b=20),
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---") # Garis pembatas
        
        # 2. Menampilkan Tabel di Bawah Grafik
        st.markdown("#### Tabel Data Ringkasan")
        # Sekarang kita bisa memasukkan kolom 'Rentang Tanggal' karena layarnya luas
        df_ringkasan_tabel = df_ringkasan[['Bulan - Minggu', 'Rentang Tanggal', 'Growth IPH (%)', 'Arah']].copy()
        
        # Membalik urutan agar minggu terbaru selalu di baris teratas
        df_ringkasan_tabel = df_ringkasan_tabel.iloc[::-1]
        
        # Styling untuk arah
        def color_arah(val):
            if str(val) == 'Naik':
                return 'color: #ff4b4b; font-weight: bold;'
            elif str(val) == 'Turun':
                return 'color: #09ab3b; font-weight: bold;'
            return ''
        
        # Format angka
        def format_growth(val):
            try:
                return f"{float(val):.3f}%"
            except:
                return val
        
        df_ringkasan_tabel['Growth IPH (%)'] = df_ringkasan_tabel['Growth IPH (%)'].apply(format_growth)
            
        # Tampilkan tabel full width
        st.dataframe(df_ringkasan_tabel.style.map(color_arah, subset=['Arah']), 
                     use_container_width=True, hide_index=True)

    # ==========================================
    # TAB 2: TOP 5 ANDIL
    # ==========================================
    with tab2:
        st.markdown("#### Tabel Top 5 Komoditas Penyumbang Andil per Minggu")
        list_minggu = df_top5['Minggu'].unique()
        
        if len(list_minggu) > 0:
            # Filter diletakkan berdampingan dengan tabel
            col_filter, col_space = st.columns([1, 2])
            with col_filter:
                selected_minggu = st.selectbox("Pilih Periode Minggu:", reversed(list_minggu))
                
            filtered_top5 = df_top5[df_top5['Minggu'] == selected_minggu].drop(columns=['Minggu'])
            
            def style_keterangan_andil(row):
                if 'KENAIKAN' in str(row['Keterangan']):
                    return ['color: #ff4b4b; font-weight: bold;'] * len(row)
                elif 'PENURUNAN' in str(row['Keterangan']):
                    return ['color: #09ab3b; font-weight: bold;'] * len(row)
                return [''] * len(row)

            st.dataframe(filtered_top5.style.apply(style_keterangan_andil, axis=1), use_container_width=True, hide_index=True)
            
else:
    st.warning("Data belum berhasil diproses. Pastikan file di dalam `data_arsip/` memiliki format sheet 'Ringkasan' dan 'Top 5'.")