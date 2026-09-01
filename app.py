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
# --- FUNGSI UNTUK MENGGABUNGKAN SELURUH DATA DARI ARSIP ---
def load_all_data():
    all_files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))
    
    list_ringkasan = []
    list_top5 = []
    
    for file in all_files:
        try:
            with pd.ExcelFile(file, engine='openpyxl') as xls:
                # 1. Load Ringkasan
                sheet_ringkasan = [s for s in xls.sheet_names if "ringkasan" in s.lower()]
                if sheet_ringkasan:
                    df_r = pd.read_excel(xls, sheet_name=sheet_ringkasan[0], skiprows=2)
                    if 'Bulan - Minggu' in df_r.columns:
                        df_r = df_r.dropna(subset=['Bulan - Minggu'])
                        list_ringkasan.append(df_r)
                    else:
                        st.sidebar.error(f"Kolom 'Bulan - Minggu' tidak ditemukan di {os.path.basename(file)}.")
                
                # 2. Load Top 5
                # Dibuat lebih longgar jika penamaan sheet-nya "Top5", "Top 5", atau "Andil"
                sheet_top5 = [s for s in xls.sheet_names if "top 5" in s.lower() or "top5" in s.lower() or "andil" in s.lower()]
                if sheet_top5:
                    df_t_raw = pd.read_excel(xls, sheet_name=sheet_top5[0], header=None)
                    current_week = None
                    for index, row in df_t_raw.iterrows():
                        val_asli = str(row[0]).strip()
                        # Mengubah teks sementara menjadi HURUF BESAR SEMUA untuk pengecekan
                        val_upper = val_asli.upper() 
                        
                        # LOGIKA BARU: Kebal huruf besar/kecil, mengecek keberadaan kata "MINGGU" dan penanda waktu
                        if "MINGGU" in val_upper and ("S/D" in val_upper or "202" in val_upper or "-" in val_upper):
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
    file_bytes = uploaded_file.getvalue()
    
    # Deteksi pintar: Cek apakah file sudah ada dan isinya sama persis
    is_new = True
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            if f.read() == file_bytes:
                is_new = False # File sudah ada dan sama, tidak perlu di-refresh ulang
                
    if is_new:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        st.sidebar.success(f"Data baru dari '{uploaded_file.name}' berhasil diproses!")
        import time
        time.sleep(1) # Memberi jeda 1 detik agar server cloud selesai menyimpan
        st.rerun()
    else:
        st.sidebar.success(f"File '{uploaded_file.name}' sedang aktif digunakan.")

st.sidebar.markdown("---")
st.sidebar.markdown("**File Tersimpan di Server:**")

# Fungsi Pop-up Dialog untuk Konfirmasi Hapus
@st.dialog("⚠️ Konfirmasi Hapus File")
def hapus_file_dialog(nama_file):
    st.warning(f"Apakah Anda yakin ingin menghapus file **{nama_file}**?")
    st.markdown("Data bulan terkait akan ikut terhapus dari tabel dan grafik dashboard.")
    
    col_ya, col_batal = st.columns(2)
    with col_ya:
        if st.button("Ya, Hapus Data", type="primary", use_container_width=True):
            file_path_hapus = os.path.join(DATA_DIR, nama_file)
            if os.path.exists(file_path_hapus):
                try:
                    os.remove(file_path_hapus)
                    st.rerun() # Refresh HANYA jika sukses dihapus
                except Exception as e:
                    st.error(f"Gagal menghapus file. Error: {e}") # Munculkan pesan error jika gagal
    
    with col_batal:
        if st.button("Batal", use_container_width=True):
            st.rerun()

# Menampilkan daftar file beserta tombol Hapus
for f_name in os.listdir(DATA_DIR):
    if f_name.endswith(".xlsx"):
        col_nama, col_tombol = st.sidebar.columns([5, 1])
        with col_nama:
            st.caption(f"📄 {f_name}")
        with col_tombol:
            # Membuat tombol X yang unik untuk setiap file menggunakan parameter 'key'
            if st.button("❌", key=f"del_{f_name}", help=f"Hapus {f_name}"):
                hapus_file_dialog(f_name)

# --- MEMUAT DATA ---
df_ringkasan, df_top5 = load_all_data()

# Ekstrak Tahun menggunakan Regex (mengambil 4 digit angka berurutan) untuk keperluan Filter
if not df_ringkasan.empty:
    df_ringkasan['Tahun'] = df_ringkasan['Bulan - Minggu'].astype(str).str.extract(r'(\d{4})')
if not df_top5.empty:
    df_top5['Tahun'] = df_top5['Minggu'].astype(str).str.extract(r'(\d{4})')

# --- TAMPILAN UTAMA (MENGGUNAKAN TABS) ---
if not df_ringkasan.empty and not df_top5.empty:
    
    # Menyiapkan data metrik terbaru (dari keseluruhan data)
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
    
    # MEMBUAT TABS
    tab1, tab2 = st.tabs(["📈 Ringkasan & Tren IPH", "🔥 Top 5 Andil Komoditas"])
    
    # ==========================================
    # TAB 1: GRAFIK TREN & TABEL RINGKASAN
    # ==========================================
    with tab1:
        # FILTER TAHUN UNTUK TAB 1
        list_tahun = sorted(df_ringkasan['Tahun'].dropna().unique().tolist(), reverse=True)
        opsi_tahun_tab1 = ["Semua"] + list_tahun
        selected_tahun_tab1 = st.selectbox("🗓️ Pilih Periode Data:", opsi_tahun_tab1, key="filter_tab1")
        
        # Terapkan filter pada dataframe
        if selected_tahun_tab1 == "Semua":
            df_ringkasan_filtered = df_ringkasan.copy()
        else:
            df_ringkasan_filtered = df_ringkasan[df_ringkasan['Tahun'] == selected_tahun_tab1].copy()

        # 1. Menampilkan Grafik Lebar Penuh
        st.markdown("#### Tren Historis Growth IPH")
        df_ringkasan_filtered['Growth IPH (%)'] = pd.to_numeric(df_ringkasan_filtered['Growth IPH (%)'], errors='coerce')
        
        fig = px.line(df_ringkasan_filtered, x='Bulan - Minggu', y='Growth IPH (%)', markers=True, 
                      hover_data=['Rentang Tanggal', 'Arah'])
        
        # Menyambungkan garis yang putus jika ada data kosong
        fig.update_traces(
            line=dict(color='#F58220', width=3), 
            marker=dict(size=8, color='#022B69'),
            connectgaps=True 
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.8)
        fig.update_layout(xaxis_title="", yaxis_title="Growth IPH (%)", margin=dict(t=10, b=20),
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 2. Menampilkan Tabel di Bawah Grafik
        st.markdown("#### Tabel Data Ringkasan")
        df_ringkasan_tabel = df_ringkasan_filtered[['Bulan - Minggu', 'Rentang Tanggal', 'Growth IPH (%)', 'Arah']].copy()
        
        # Membalik urutan agar minggu terbaru di atas
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
            
        st.dataframe(df_ringkasan_tabel.style.map(color_arah, subset=['Arah']), 
                     use_container_width=True, hide_index=True)


    # ==========================================
    # TAB 2: TOP 5 ANDIL
    # ==========================================
    with tab2:
        st.markdown("#### Tabel Top 5 Komoditas Penyumbang Andil per Minggu")
        
        list_tahun_top5 = sorted(df_top5['Tahun'].dropna().unique().tolist(), reverse=True)
        
        if len(list_tahun_top5) > 0:
            # MEMBUAT FILTER BERTINGKAT (CASCADING DROPDOWN)
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                selected_tahun_tab2 = st.selectbox("1️⃣ Pilih Tahun:", list_tahun_top5, key="filter_tab2_tahun")
                
            # Filter Data Top 5 berdasarkan tahun yang dipilih
            df_top5_year = df_top5[df_top5['Tahun'] == selected_tahun_tab2]
            list_minggu = df_top5_year['Minggu'].unique()
            
            with col_filter2:
                selected_minggu = st.selectbox("2️⃣ Pilih Periode Minggu:", reversed(list_minggu), key="filter_tab2_minggu")
                
            # Menghapus kolom Minggu dan Tahun sebelum ditampilkan ke tabel
            filtered_top5 = df_top5_year[df_top5_year['Minggu'] == selected_minggu].drop(columns=['Minggu', 'Tahun'])
            
            def style_keterangan_andil(row):
                if 'KENAIKAN' in str(row['Keterangan']):
                    return ['color: #ff4b4b; font-weight: bold;'] * len(row)
                elif 'PENURUNAN' in str(row['Keterangan']):
                    return ['color: #09ab3b; font-weight: bold;'] * len(row)
                return [''] * len(row)

            st.markdown("<br>", unsafe_allow_html=True) # Tambah sedikit jarak
            st.dataframe(filtered_top5.style.apply(style_keterangan_andil, axis=1), use_container_width=True, hide_index=True)
            
else:
    st.warning("Data belum berhasil diproses. Pastikan file di dalam folder `data_arsip/` memiliki format sheet 'Ringkasan' dan 'Top 5'.")