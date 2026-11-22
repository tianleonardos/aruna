"""Beranda Utama (Landing Page & Gateway) Proyek ARUNA.

Fitur:
1. Tampilan Login Tunggal di awal: saat pengguna belum login, hanya menampilkan form masuk/daftar tanpa konten lain.
2. Identitas visual resmi dengan logo assets/icon_logo.svg dan tipografi 'Alan Sans Semibold' warna #5A069A.
3. Tampilan Mahasiswa: Dilengkapi visualisasi sederhana kondisi kesehatan mental terakhir berdasarkan asesmen terakhirnya.
4. Tampilan Admin: Menyediakan akses instan ke seluruh modul manajemen dan CMS.
"""

from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from src.theme import (
    apply_theme,
    get_vector,
    get_logo_base64,
)
from src.database import (
    initialize_database,
    authenticate_user,
    register_user,
    get_assessment_history,
    get_announcements,
    get_support_contacts,
    get_faqs,
)

# Inisialisasi database dan baca sesi aktif
initialize_database()
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# Atur visibilitas sidebar: disembunyikan untuk tamu dan mahasiswa
apply_theme(hide_sidebar=not is_admin)

logo_data_uri = get_logo_base64()


# ===========================================================================
# 1. GATEWAY LOGIN AWAL (HANYA DITAMPILKAN JIKA BELUM LOGIN)
# ===========================================================================

if not current_user:
    # Kontainer terpusat untuk pengalaman login yang bersih, modern & elegan
    st.write("")
    st.write("")
    col_l, col_center, col_r = st.columns([1, 2.2, 1])

    with col_center:
        # Logo dan Header Branding
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 24px;">
                <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 86px; height: 86px; object-fit: contain; margin-bottom: 12px;" />
                <h1 class="aruna-brand-title" style="font-size: 3.2rem; margin: 0; line-height: 1;">Aruna</h1>
                <div style="font-size: 1.12rem; font-weight: 600; color: #5A069A; margin-top: 6px;">
                    Mental Well-Being Profiling System
                </div>
                <p style="font-size: 0.92rem; color: var(--text-color); opacity: 0.75; margin-top: 6px; line-height: 1.5;">
                    Pemetaan profil kesejahteraan mental mahasiswa berbasis <em>Mental Health Continuum-Short Form (MHC-SF)</em> dan Unsupervised Machine Learning.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Form Otentikasi
        auth_tab_login, auth_tab_reg = st.tabs(["🔑 Masuk Akun", "📝 Registrasi Mahasiswa Baru"])

        with auth_tab_login:
            st.caption("Masuk untuk melakukan asesmen atau meninjau riwayat profil Anda.")
            with st.form("form_login_gateway"):
                l_user = st.text_input("Username:", placeholder="Masukkan username Anda...")
                l_pass = st.text_input("Password:", type="password", placeholder="Masukkan password...")
                btn_login = st.form_submit_button("Masuk ke Portal Aruna ✨", type="primary", use_container_width=True)

                if btn_login:
                    user_data = authenticate_user(l_user, l_pass)
                    if user_data:
                        st.session_state["user"] = user_data
                        st.success(f"Selamat datang kembali, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Username atau password salah. Silakan coba kembali.")

            st.markdown(
                """
                <div style="text-align: center; margin-top: 14px; font-size: 0.82rem; color: var(--text-color); opacity: 0.7;">
                    Akses Administrator Pengujian: <code>username: admin</code> | <code>password: admin123</code>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with auth_tab_reg:
            st.caption("Pendaftaran akun mandiri untuk mahasiswa universitas.")
            with st.form("form_register_gateway"):
                r_name = st.text_input("Nama Lengkap:", placeholder="Contoh: Budi Santoso")
                r_nim = st.text_input("NIM Mahasiswa:", placeholder="Contoh: 2101234567")
                r_user = st.text_input("Pilih Username:", placeholder="Contoh: budi_s")
                r_pass = st.text_input("Pilih Password:", type="password", placeholder="Minimal 6 karakter...")
                btn_reg = st.form_submit_button("Daftar Akun Mahasiswa 🎓", type="primary", use_container_width=True)

                if btn_reg:
                    try:
                        new_u = register_user(r_user, r_pass, r_name, role="student", nim=r_nim)
                        st.session_state["user"] = new_u
                        st.success(f"Akun berhasil dibuat! Selamat datang, {new_u['full_name']}.")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

    # HENTIKAN RENDERING DI SINI SAAT BELUM LOGIN:
    # Memastikan tidak ada konten portal lain yang bocor sebelum pengguna login.
    st.stop()


# ===========================================================================
# 2. HEADER RESMI UNTUK PENGGUNA TEROTENTIKASI
# ===========================================================================

h_col1, h_col2 = st.columns([3, 1.2], vertical_alignment="center")

with h_col1:
    badge_label = "👑 Administrator & Peneliti" if is_admin else "🎓 Mahasiswa Aktif"
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 16px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 52px; height: 52px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">{badge_label}</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.2rem; line-height: 1.1;">Aruna</h1>
                <div style="font-size: 0.95rem; color: var(--text-color); opacity: 0.8; margin-top: 2px;">
                    Pemetaan Profil Kesejahteraan Mental Mahasiswa
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with h_col2:
    st.markdown(
        f"""
        <div style="text-align: right;">
            <div style="font-weight: 700; color: #5A069A; font-size: 1.05rem;">{current_user['full_name']}</div>
            <div style="font-size: 0.82rem; color: var(--text-color); opacity: 0.7;">@{current_user['username']} {f'· NIM: {current_user["nim"]}' if current_user.get('nim') else ''}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Keluar (Logout) 🚪", key="btn_logout_top", use_container_width=True):
        st.session_state.pop("user", None)
        st.session_state.pop("assessment_result", None)
        st.rerun()

st.divider()


# ===========================================================================
# 3. TAMPILAN BERANDA MAHASISWA DENGAN VISUALISASI KONDISI TERAKHIR
# ===========================================================================

if not is_admin:
    user_id = current_user.get("id")
    # Ambil riwayat asesmen terbaru mahasiswa ini
    user_history = get_assessment_history(limit=1, user_id=user_id)

    # Jika riwayat spesifik user belum ada, cek fallback riwayat umum jika ada
    if not user_history:
        fallback_history = get_assessment_history(limit=1)
    else:
        fallback_history = []

    latest_assessment = user_history[0] if user_history else (fallback_history[0] if fallback_history else None)

    # -----------------------------------------------------------------------
    # A. VISUALISASI KONDISI KESEJAHTERAAN TERAKHIR MAHASISWA
    # -----------------------------------------------------------------------
    if latest_assessment:
        try:
            created_dt = datetime.fromisoformat(latest_assessment["created_at"])
            formatted_date = created_dt.strftime("%d %B %Y, %H:%M WIB")
        except Exception:
            formatted_date = latest_assessment["created_at"]

        e_score = float(latest_assessment["emotional"])
        s_score = float(latest_assessment["social"])
        p_score = float(latest_assessment["psychological"])

        st.markdown(
            f"""
            <div class="aruna-card" style="border-left: 6px solid #5A069A; padding: 26px 30px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <span class="aruna-badge">Kondisi Kesejahteraan Mental Terakhir</span>
                        <h2 style="margin: 4px 0 6px 0; color: #5A069A; font-size: 1.6rem;">
                            {latest_assessment['overall_profile']} · {latest_assessment['pattern_profile']}
                        </h2>
                        <div style="font-size: 0.85rem; color: var(--text-color); opacity: 0.75;">
                            📅 Waktu Asesmen Terakhir: <strong>{formatted_date}</strong>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span class="aruna-badge-sunset">Skala MHC-SF (0–5)</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Kartu Visualisasi 3 Dimensi Sederhana
        st.markdown("#### 📈 Visualisasi Dinamika 3 Dimensi Kesejahteraan")
        c_emo, c_soc, c_psy = st.columns(3)

        with c_emo:
            st.metric("Dimensi Emosional", f"{e_score:.2f} / 5.00")
            st.progress(max(0.0, min(e_score / 5.0, 1.0)))
            st.caption("Perasaan positif, kebahagiaan, dan kepuasan terhadap hidup.")

        with c_soc:
            st.metric("Dimensi Sosial", f"{s_score:.2f} / 5.00")
            st.progress(max(0.0, min(s_score / 5.0, 1.0)))
            st.caption("Rasa penerimaan, integrasi, dan keterhubungan dalam masyarakat.")

        with c_psy:
            st.metric("Dimensi Psikologis", f"{p_score:.2f} / 5.00")
            st.progress(max(0.0, min(p_score / 5.0, 1.0)))
            st.caption("Pengembangan diri, tujuan hidup, dan penerimaan diri secara utuh.")

        # Grafik Bar Horizontal Perbandingan Dimensi
        chart_df = pd.DataFrame({
            "Skor Rata-rata": [e_score, s_score, p_score]
        }, index=["Emosional", "Sosial", "Psikologis"])

        with st.expander("📊 Lihat Diagram Perbandingan Dimensi & Catatan Fokus", expanded=True):
            st.bar_chart(chart_df, color="#5A069A", horizontal=True)
            st.markdown(
                f"""
                <div class="aruna-helper-box">
                    <strong style="color: #5A069A;">💡 Fokus Rekomendasi Terakhir:</strong> {latest_assessment.get('focus', 'Penyelarasan Kesejahteraan')}<br>
                    <span style="opacity: 0.9;">{latest_assessment.get('summary', '')}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Tombol Aksi Cepat Mahasiswa
        nav_btn1, nav_btn2 = st.columns(2)
        with nav_btn1:
            st.page_link(
                "pages/6_Student_Assessment.py",
                label="📝 Mulai Asesmen Ulang (Mode Flashcard)",
                icon="✨",
                use_container_width=True,
            )
        with nav_btn2:
            st.page_link(
                "pages/7_Student_History.py",
                label="📊 Lihat Riwayat & Seluruh Rekomendasi",
                icon="📈",
                use_container_width=True,
            )

    else:
        # Jika belum ada asesmen sama sekali
        st.markdown(
            f"""
            <div class="aruna-card" style="border-left: 6px solid #5A069A; padding: 28px;">
                <div style="display: flex; gap: 20px; align-items: center;">
                    <div style="max-width: 90px; flex-shrink: 0;">
                        {get_vector("flourishing_mind")}
                    </div>
                    <div>
                        <span class="aruna-badge">Selamat Datang</span>
                        <h2 style="margin: 4px 0 8px 0; color: #5A069A;">Halo, {current_user['full_name']}! 🌱</h2>
                        <p style="color: var(--text-color); opacity: 0.85; margin: 0; line-height: 1.6;">
                            Anda belum pernah melakukan asesmen kesejahteraan mental. Luangkan waktu 3–5 menit untuk merefleksikan 14 pertanyaan sederhana mengenai kondisi emosional, sosial, dan psikologis Anda selama sebulan terakhir.
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/6_Student_Assessment.py",
            label="✨ Mulai Asesmen MHC-SF Pertama Anda",
            icon="📝",
            use_container_width=True,
        )

    # -----------------------------------------------------------------------
    # B. KONTEN EDUKASI & INFORMASI KAMPUS (DARI CMS)
    # -----------------------------------------------------------------------
    st.divider()

    # 1. Pengumuman Terkini
    announcements = get_announcements(active_only=True)
    if announcements:
        st.subheader("📢 Informasi & Berita Terkini")
        for ann in announcements[:3]:
            st.markdown(
                f"""
                <div class="aruna-card" style="padding: 18px 22px; margin-bottom: 12px; border-left: 4px solid #5A069A;">
                    <h4 style="margin: 0; color: #5A069A;">{ann['title']}</h4>
                    <p style="color: var(--text-color); opacity: 0.85; font-size: 0.94rem; margin: 8px 0;">{ann['content']}</p>
                    <div style="font-size: 0.8rem; color: var(--text-color); opacity: 0.6;">Diterbitkan: {ann['created_at']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 2. Layanan Konseling & Bantuan Darurat
    contacts = get_support_contacts(active_only=True)
    if contacts:
        st.subheader("📞 Layanan Konseling & Bantuan Darurat")
        c_cols = st.columns(len(contacts[:3]))
        for idx, c in enumerate(contacts[:3]):
            with c_cols[idx]:
                st.markdown(
                    f"""
                    <div class="aruna-card" style="padding: 18px;">
                        <span class="aruna-badge">{c['category']}</span>
                        <h4 style="margin: 6px 0; color: #5A069A; font-size: 1.05rem;">{c['name']}</h4>
                        <div style="color: #EA580C; font-weight: 700; font-size: 1.15rem; margin: 6px 0;">📞 {c['phone']}</div>
                        <p style="font-size: 0.85rem; color: var(--text-color); opacity: 0.8; margin: 0;">{c['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # 3. FAQ Edukasi Kesehatan Mental
    faqs = get_faqs(active_only=True)
    if faqs:
        st.subheader("❓ Tanya Jawab Edukasi Kesejahteraan (FAQ)")
        for item in faqs:
            with st.expander(f"[{item['category']}] {item['question']}"):
                st.write(item["answer"])


# ===========================================================================
# 4. TAMPILAN BERANDA ADMINISTRATOR
# ===========================================================================

else:
    st.markdown(
        f"""
        <div class="aruna-card" style="border-left: 6px solid #5A069A; padding: 24px;">
            <span class="aruna-badge">Pusat Kendali Sistem</span>
            <h2 style="margin: 6px 0 10px 0; color: #5A069A;">Selamat Datang di Portal Administrator Aruna</h2>
            <p style="color: var(--text-color); opacity: 0.85; margin: 0; line-height: 1.6;">
                Gunakan menu sidebar atau tombol akses cepat di bawah ini untuk memantau data asesmen mahasiswa, mengelola konten website, memperbarui dataset referensi, serta melatih dan mengevaluasi model Machine Learning.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Akses Cepat Modul Administrator")
    ac_col1, ac_col2, ac_col3 = st.columns(3)

    with ac_col1:
        st.page_link("pages/1_Admin_Dashboard.py", label="Admin Dashboard & Audit Asesmen", icon="🏠", use_container_width=True)
        st.page_link("pages/8_Website_CRUD.py", label="Manajemen Konten (CMS)", icon="✏️", use_container_width=True)

    with ac_col2:
        st.page_link("pages/3_Model_Training.py", label="Pelatihan Model (One-Click)", icon="⚙️", use_container_width=True)
        st.page_link("pages/2_Dataset_Management.py", label="Manajemen Dataset Referensi", icon="📁", use_container_width=True)

    with ac_col3:
        st.page_link("pages/4_Model_Evaluation.py", label="Evaluasi & Perbandingan Model", icon="📈", use_container_width=True)
        st.page_link("pages/5_Model_Registry.py", label="Model Registry & Versi Aktif", icon="🗃️", use_container_width=True)
