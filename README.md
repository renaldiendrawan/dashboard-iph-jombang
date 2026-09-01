# 📊 EWANGI - Dashboard Early Warning IPH
**Badan Pusat Statistik (BPS) Kabupaten Jombang**

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

Aplikasi berbasis web interaktif (*Executive Dashboard*) yang dirancang untuk memantau pergerakan Indeks Perkembangan Harga (IPH) mingguan. Aplikasi ini berfungsi sebagai sistem peringatan dini (*early warning system*) bagi pemerintah daerah dan pengambil kebijakan di Kabupaten Jombang untuk mengendalikan inflasi daerah secara responsif.

## ✨ Fitur Utama

*   **Integrasi Basis Data Cloud (*Real-time*):** Mengambil data secara langsung dari Google Sheets. Admin BPS hanya perlu memperbarui data di *spreadsheet*, dan dashboard akan otomatis menyesuaikan visualisasinya tanpa perlu mengubah kode.
*   **Indikator Kinerja Utama (KPI):** Menampilkan metrik krusial secara instan (Periode Terakhir, Growth IPH Terkini, dan Status Tren) di bagian teratas.
*   **Grafik Tren Historis Dinamis:** Visualisasi garis (menggunakan Plotly) yang melacak fluktuasi IPH Mingguan. Dilengkapi fitur filter cerdas untuk melihat tren gabungan seluruh tahun atau tahun spesifik (misal: 2025, 2026).
*   **Analisis Top 5 Penyumbang Andil:** Modul khusus dengan *cascading dropdown* (Pilih Tahun ➡️ Pilih Minggu) untuk menyoroti 5 komoditas utama yang menjadi penyumbang terbesar kenaikan (inflasi) atau penurunan (deflasi) harga.
*   **Pewarnaan Otomatis (*Conditional Formatting*):** Tabel data dirancang agar mudah dibaca secara cepat; warna merah untuk tren/andil naik, dan warna hijau untuk tren/andil turun.

## ⚙️ Cara Kerja Sistem Data
Dashboard ini menggunakan metode pembacaan tautan publik (`/export?format=xlsx`) dari Google Sheets. Sistem dibangun agar mendukung struktur *multi-link*, sehingga arsip data dari berbagai tahun (misal: 2025 dan 2026 yang terpisah file) dapat disatukan (*concatenate*) secara mulus di latar belakang aplikasi.

## 🚀 Panduan Instalasi (Lokal)

Jika Anda ingin menjalankan atau mengembangkan aplikasi ini di komputer lokal, ikuti langkah-langkah berikut:

**1. Clone Repositori**
```bash
git clone [https://github.com/renaldiendrawan/dashboard-iph-jombang.git](https://github.com/renaldiendrawan/dashboard-iph-jombang.git)

```

**2. Persiapan Dependensi**
Pastikan Anda sudah menginstal Python (minimal versi 3.8). Instal seluruh pustaka yang dibutuhkan menggunakan perintah:

```bash
pip install -r requirements.txt

```

**3. Konfigurasi Google Sheets**
Buka file `app.py`, lalu cari variabel `GOOGLE_SHEETS_URLS`. Masukkan tautan Google Sheets Anda di sana. Pastikan akses tautan Google Sheets sudah diubah menjadi **"Siapa saja yang memiliki link" (Viewer)** dan akhir tautannya diubah menjadi `/export?format=xlsx`.

**4. Jalankan Aplikasi**

```bash
streamlit run app.py

```

Aplikasi akan otomatis terbuka di *browser* Anda pada alamat `http://localhost:8501`.

## 📂 Struktur Direktori

```text
📦 ewangi-dashboard
 ┣ 📂 assets/
 ┃ ┗ 📜 logo_bps.png       # Logo BPS yang tampil di sudut kiri atas aplikasi
 ┣ 📜 app.py               # Kode utama backend & frontend (Streamlit)
 ┣ 📜 requirements.txt     # Daftar modul Python (streamlit, pandas, plotly, dll)
 ┗ 📜 README.md            # Dokumentasi proyek ini

```

## 👨‍💻 Pengembang

Dikembangkan untuk **Badan Pusat Statistik Kabupaten Jombang**.
