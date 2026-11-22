"""Entry Point Aplikasi Streamlit ARUNA.

Mengatur:
1. Konfigurasi halaman global, ikon logo resmi, dan sinkronisasi tema Dark/Light mode.
2. Akses Gate Otentikasi: Saat belum login, pengguna hanya diarahkan ke layar login tunggal.
3. Kebijakan Sidebar: Sidebar hanya muncul untuk akun Administrator. Untuk mahasiswa, sidebar disembunyikan dan navigasi menggunakan tombol in-page.
4. Hak Akses (Role-Based Access Control).
"""

from __future__ import annotations
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from src.theme import apply_theme, get_logo_file_path
from src.database import initialize_database

logo_file = get_logo_file_path()

# 1. Konfigurasi halaman global utama dengan icon logo resmi (PNG/SVG)
st.set_page_config(
    page_title="Aruna · Mental Well-Being Profiling",
    page_icon=logo_file,
    layout="wide",
)

initialize_database()

# 2. Cek sesi login & tentukan hak akses
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# 3. Terapkan tema: Sembunyikan sidebar untuk mahasiswa/tamu, tampilkan untuk admin
apply_theme(hide_sidebar=not is_admin)

# 4. Tampilkan sidebar HANYA jika akun adalah Administrator
if is_admin:
    if logo_file != "🌱":
        st.logo(logo_file, icon_image=logo_file)

    with st.sidebar:
        st.markdown(
            f"""
            <div style="background: var(--secondary-background-color); padding: 14px; border-radius: 14px; border: 1px solid rgba(90,6,154,0.22); margin-bottom: 14px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #5A069A; text-transform: uppercase;">👑 Administrator</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-color); margin-top: 2px;">{current_user['full_name']}</div>
                <div style="font-size: 0.8rem; color: var(--text-color); opacity: 0.7;">@{current_user['username']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Keluar Akun Admin", key="sidebar_logout_btn", use_container_width=True):
            st.session_state.pop("user", None)
            st.rerun()

# 5. Konfigurasi Struktur Navigasi Halaman
# PERHATIAN: Parameter 'icon' pada st.Page WAJIB berupa emoji atau Material icon shortcode, BUKAN path file gambar.
if not current_user:
    # Belum Login: HANYA akses halaman Login di awal tanpa menampilkan modul lainnya
    pages = {
        "Autentikasi": [
            st.Page("pages/0_Home.py", title="Masuk ke Aruna", icon="✨", default=True),
        ]
    }
elif is_admin:
    # Navigasi Lengkap Khusus Administrator
    pages = {
        "Beranda": [
            st.Page("pages/0_Home.py", title="Beranda Utama", icon="🌱", default=True),
        ],
        "Administrator & Peneliti": [
            st.Page("pages/1_Admin_Dashboard.py", title="Admin Dashboard", icon="🏠"),
            st.Page("pages/8_Website_CRUD.py", title="Manajemen Konten (CMS)", icon="✏️"),
            st.Page("pages/2_Dataset_Management.py", title="Manajemen Dataset", icon="📁"),
            st.Page("pages/3_Model_Training.py", title="Model Training", icon="⚙️"),
            st.Page("pages/4_Model_Evaluation.py", title="Evaluasi & Perbandingan", icon="📈"),
            st.Page("pages/5_Model_Registry.py", title="Model Registry & Versi", icon="🗃️"),
        ],
        "Pratinjau Mahasiswa": [
            st.Page("pages/6_Student_Assessment.py", title="Pratinjau Asesmen", icon="📝"),
            st.Page("pages/7_Student_History.py", title="Semua Riwayat Asesmen", icon="📊"),
        ],
    }
else:
    # Navigasi Mahasiswa (Sidebar otomatis disembunyikan via CSS, navigasi via tombol)
    pages = {
        "Mahasiswa": [
            st.Page("pages/0_Home.py", title="Beranda Mahasiswa", icon="🌱", default=True),
            st.Page("pages/6_Student_Assessment.py", title="Asesmen MHC-SF", icon="📝"),
            st.Page("pages/7_Student_History.py", title="Riwayat Asesmen", icon="📊"),
        ],
    }

navigation = st.navigation(pages)
navigation.run()
