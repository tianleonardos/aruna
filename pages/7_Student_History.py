"""Halaman Riwayat Asesmen Mahasiswa ARUNA.

Menyediakan:
1. Riwayat asesmen mahasiswa berurutan dari waktu terbaru.
2. Tampilan visual skor tiga dimensi dan rekomendasi masa lalu.
3. Navigasi berbasis tombol (sidebar disembunyikan untuk mahasiswa).
4. Kode unik disembunyikan untuk mahasiswa (hanya tersimpan untuk audit admin).
"""

from __future__ import annotations
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from src.theme import apply_theme, get_vector, get_logo_base64
from src.database import (
    initialize_database,
    get_assessment_history,
    get_assessment_by_id,
)

# Cek peran pengguna untuk menentukan visibilitas sidebar
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

apply_theme(hide_sidebar=not is_admin)
initialize_database()

# Tombol Kembali ke Beranda (Navigasi Pengganti Sidebar)
st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda", icon="🏠")

logo_data_uri = get_logo_base64()

# Header Halaman
header_col1, header_col2 = st.columns([3, 1], vertical_alignment="center")

with header_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">Refleksi Mandiri</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Riwayat Asesmen Mahasiswa")
    st.caption("Lihat kembali dinamika profil dan skor kesejahteraan mental yang pernah Anda lakukan.")

with header_col2:
    st.markdown(
        f'<div style="max-width: 130px; margin: auto;">{get_vector("student_journey")}</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ==================================================
# DAFTAR RIWAYAT
# ==================================================

user_id = current_user.get("id") if current_user else None

# Ambil riwayat asesmen
history = get_assessment_history(limit=100, user_id=user_id)

if not history:
    st.info(
        "🌱 Belum ada riwayat asesmen yang tercatat. "
        "Silakan lakukan asesmen MHC-SF pertama Anda."
    )
    st.page_link(
        "pages/6_Student_Assessment.py",
        label="Mulai Asesmen MHC-SF Sekarang",
        icon="📝",
    )
    st.stop()

# Ringkasan Cepat
latest = history[0]
c_met1, c_met2, c_met3 = st.columns(3)
with c_met1:
    st.metric("Total Asesmen Dilakukan", f"{len(history)} Kali")
with c_met2:
    st.metric(
        "Asesmen Terakhir",
        pd.to_datetime(latest["created_at"]).strftime("%d %b %Y, %H:%M"),
    )
with c_met3:
    st.metric("Profil Terakhir", f"{latest['overall_profile']} - {latest['pattern_profile']}")

# Tabel Riwayat (Kode Unik disembunyikan untuk mahasiswa, hanya tampil jika admin)
st.subheader("Daftar Rekam Jejak Asesmen")
t_rows = []
for idx, item in enumerate(history, start=1):
    row_data = {
        "No": idx,
        "Waktu": pd.to_datetime(item["created_at"]).strftime("%d/%m/%Y %H:%M"),
        "Profil Keseluruhan": item["overall_profile"],
        "Pola Dimensi": item["pattern_profile"],
        "Emosional": f"{item['emotional']:.2f}",
        "Sosial": f"{item['social']:.2f}",
        "Psikologis": f"{item['psychological']:.2f}",
    }
    # Kode unik hanya ditampilkan untuk keperluan audit admin
    if is_admin:
        row_data["Kode Unik (Admin)"] = item.get("unique_code", f"ARN-{item['id']}")

    t_rows.append(row_data)

st.dataframe(pd.DataFrame(t_rows), use_container_width=True, hide_index=True)


# ==================================================
# DETAIL HASIL ASESMEN PILIHAN
# ==================================================

st.divider()
st.subheader("Inspeksi Rincian Asesmen")

opts = {
    item["id"]: f"Asesmen #{len(history) - idx + 1} — {pd.to_datetime(item['created_at']).strftime('%d %B %Y, %H:%M')} [{item['overall_profile']} - {item['pattern_profile']}]"
    for idx, item in enumerate(history)
}

selected_id = st.selectbox(
    "Pilih waktu asesmen untuk melihat rincian:",
    options=list(opts.keys()),
    format_func=lambda x: opts[x],
)

selected = get_assessment_by_id(selected_id)

if selected:
    st.markdown(
        f"""
        <div class="aruna-card">
            <span class="aruna-badge">Hasil Asesmen</span>
            <h3 style="margin-top: 10px; color: #5A069A;">{selected['recommendation_profile']}</h3>
            <p style="color: var(--text-color); opacity: 0.85; line-height: 1.6;">{selected['summary']}</p>
            <p style="color: #5A069A; font-weight: 600; margin-bottom: 0;">Fokus Pengembangan: {selected['focus']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    d_col1, d_col2, d_col3 = st.columns(3)
    dim_items = [
        ("Kesejahteraan Emosional", selected["emotional"], d_col1),
        ("Kesejahteraan Sosial", selected["social"], d_col2),
        ("Kesejahteraan Psikologis", selected["psychological"], d_col3),
    ]

    for label, val, col in dim_items:
        with col:
            st.metric(label, f"{val:.2f} / 5.00")
            st.progress(max(0.0, min(float(val) / 5.0, 1.0)))

    st.markdown("#### Saran Rekomendasi Terkait")
    for i, r in enumerate(selected["recommendations"], start=1):
        st.markdown(
            f"""
            <div style="background-color: var(--secondary-background-color); border: 1px solid rgba(90,6,154,0.18); padding: 12px 16px; border-radius: 10px; margin-bottom: 8px; border-left: 3px solid #5A069A; color: var(--text-color);">
                <strong style="color: #5A069A;">{i}.</strong> {r}
            </div>
            """,
            unsafe_allow_html=True,
        )
