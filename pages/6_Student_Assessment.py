"""Halaman Asesmen Kesejahteraan Mental Mahasiswa (MHC-SF).

Menyediakan:
1. Pengerjaan per soal dalam bentuk Flashcard Interaktif.
2. Keterangan tambahan (panduan pemahaman) untuk setiap butir pertanyaan.
3. Animasi 3D loading bertema mental health saat memproses analisis.
4. Hasil pemetaan profil tanpa menampilkan kode unik (disimpan di backend untuk admin).
5. Navigasi berbasis tombol (sidebar disembunyikan untuk mahasiswa).
"""

from __future__ import annotations
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from src.theme import apply_theme, get_vector, render_mental_health_loader, get_logo_base64
from src.mhcsf_config import (
    INSTRUCTION,
    MHC_SF_ITEMS,
    DIMENSIONS,
    RESPONSE_OPTIONS,
)
from src.pipeline import assess_student
from src.database import (
    initialize_database,
    save_assessment,
)

# Cek peran pengguna untuk menentukan visibilitas sidebar
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

apply_theme(hide_sidebar=not is_admin)
initialize_database()

# Inisialisasi state kuesioner
if "assessment_answers" not in st.session_state:
    st.session_state["assessment_answers"] = {item["id"]: None for item in MHC_SF_ITEMS}

if "current_question_idx" not in st.session_state:
    st.session_state["current_question_idx"] = 0

response_labels = [opt["label"] for opt in RESPONSE_OPTIONS]
response_mapping = {opt["label"]: opt["value"] for opt in RESPONSE_OPTIONS}


def reset_assessment():
    """Mereset seluruh jawaban dan hasil asesmen."""
    st.session_state["assessment_answers"] = {item["id"]: None for item in MHC_SF_ITEMS}
    st.session_state["current_question_idx"] = 0
    st.session_state.pop("assessment_result", None)


# Navigasi & Header Branding
st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda", icon="🏠")

logo_data_uri = get_logo_base64()

# ===========================================================================
# JIKA SUDAH ADA HASIL ASESMEN, TAMPILKAN HASILNYA
# ===========================================================================
result = st.session_state.get("assessment_result")

if result:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">Hasil Analisis Profil Kesejahteraan</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Profil Kesejahteraan Mental Anda")
    st.caption("Pemetaan objektif berdasarkan instrumen MHC-SF dan model Unsupervised Machine Learning.")

    # Ringkasan Profil
    res_col1, res_col2 = st.columns([2, 1], vertical_alignment="center")

    with res_col1:
        st.markdown(
            f"""
            <div class="aruna-card">
                <span class="aruna-badge">Karakteristik Psikososial</span>
                <h2 style="margin: 8px 0; color: var(--text-color);">{result['recommendation']['profile_name']}</h2>
                <p style="color: var(--text-color); opacity: 0.85; font-size: 1rem; line-height: 1.6;">
                    {result['recommendation']['summary']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with res_col2:
        st.markdown(
            f'<div style="max-width: 150px; margin: auto;">{get_vector("flourishing_mind")}</div>',
            unsafe_allow_html=True,
        )

    # Dua Tingkat Profil
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Tingkat Kesejahteraan Umum", result["overall_profile"])
    with col_m2:
        st.metric("Pola Deviasi Antardimensi", result["pattern_profile"])

    # Skor Tiga Dimensi
    st.markdown("### Skor Tiga Dimensi")
    dimension_scores = result["dimension_scores"]
    d_cols = st.columns(3)

    for idx, (dim_key, dim_info) in enumerate(DIMENSIONS.items()):
        score = dimension_scores[dim_key]
        with d_cols[idx]:
            st.markdown(
                f"""
                <div class="aruna-card" style="padding: 18px; margin-bottom: 8px;">
                    <div style="color: var(--text-color); opacity: 0.8; font-size: 0.88rem;">{dim_info['label']}</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: #5A069A; margin: 6px 0;">
                        {score:.2f} <span style="font-size: 0.9rem; font-weight: 400; opacity: 0.6;">/ 5.00</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(max(0.0, min(float(score) / 5.0, 1.0)))

    # Rekomendasi
    st.divider()
    rec = result["recommendation"]
    st.subheader("Rekomendasi Pengembangan Diri")
    st.markdown(f"**Fokus Utama:** `{rec['focus']}`")

    for i, item_sug in enumerate(rec["recommendations"], start=1):
        st.markdown(
            f"""
            <div style="background-color: var(--secondary-background-color); border: 1px solid rgba(90,6,154,0.18); padding: 14px 18px; border-radius: 12px; margin-bottom: 10px; border-left: 4px solid #5A069A;">
                <strong style="color: #5A069A;">{i}.</strong> <span style="color: var(--text-color);">{item_sug}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(f"🔒 {rec['disclaimer']}")

    action_c1, action_c2 = st.columns(2)
    with action_c1:
        st.button("Mulai Asesmen Baru", on_click=reset_assessment, type="secondary", use_container_width=True)
    with action_c2:
        st.page_link("pages/7_Student_History.py", label="Lihat Riwayat Asesmen ➡️", icon="📊", use_container_width=True)

    st.stop()


# ===========================================================================
# MODE PENGERJAAN: FLASHCARD PER SOAL
# ===========================================================================

header_c1, header_c2 = st.columns([3, 1], vertical_alignment="center")

with header_c1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">Mode Flashcard Interaktif</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Asesmen Kesejahteraan Mental")
    st.caption("Jawablah setiap butir pertanyaan dengan tenang berdasarkan pengalaman 1 bulan terakhir.")

with header_c2:
    st.markdown(
        f'<div style="max-width: 120px; margin: auto;">{get_vector("balance_harmony")}</div>',
        unsafe_allow_html=True,
    )

st.divider()

# Status Pengerjaan (Progress)
cur_idx = st.session_state["current_question_idx"]
total_items = len(MHC_SF_ITEMS)
cur_item = MHC_SF_ITEMS[cur_idx]
cur_dim = DIMENSIONS[cur_item["dimension"]]

answered_count = sum(1 for v in st.session_state["assessment_answers"].values() if v is not None)
pct_complete = int((answered_count / total_items) * 100)

st.markdown(f"**Pertanyaan {cur_idx + 1} dari {total_items}** · Terjawab: {answered_count}/{total_items} ({pct_complete}%)")
st.progress((cur_idx + 1) / total_items)

# Navigasi cepat nomor soal (chips)
chip_cols = st.columns(14)
for i in range(14):
    item_num = i + 1
    is_ans = st.session_state["assessment_answers"][item_num] is not None
    is_cur = (i == cur_idx)

    label_chip = f"● {item_num}" if is_ans else f"{item_num}"
    if chip_cols[i].button(label_chip, key=f"chip_nav_{i}", use_container_width=True):
        st.session_state["current_question_idx"] = i
        st.rerun()

# FLASHCARD UTAMA
st.markdown(
    f"""
    <div class="aruna-flashcard">
        <span class="aruna-badge" style="background: {cur_dim['color']}22 !important; color: {cur_dim['color']} !important;">
            {cur_dim['label']}
        </span>
        <h2 style="margin: 14px 0 16px 0; color: var(--text-color); font-size: 1.4rem;">
            {cur_item['question']}
        </h2>
        <div class="aruna-helper-box">
            <strong style="color: var(--text-color);">💡 Panduan Memahami Pertanyaan:</strong><br>
            <span style="color: var(--text-color); opacity: 0.85;">{cur_item['helper_text']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Pilihan Respons Jawaban
current_val = st.session_state["assessment_answers"][cur_item["id"]]
def_idx = response_labels.index(current_val) if current_val in response_labels else None

selected_choice = st.radio(
    "Pilih frekuensi yang paling sesuai:",
    options=response_labels,
    index=def_idx,
    key=f"flashcard_radio_{cur_item['id']}",
    label_visibility="collapsed",
)

st.session_state["assessment_answers"][cur_item["id"]] = selected_choice

# Tombol Navigasi Bawah
st.write("")
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

with nav_col1:
    if st.button("⬅️ Sebelumnya", disabled=(cur_idx == 0), use_container_width=True):
        st.session_state["current_question_idx"] = max(0, cur_idx - 1)
        st.rerun()

with nav_col3:
    if cur_idx < total_items - 1:
        if st.button("Berikutnya ➡️", type="primary", use_container_width=True):
            st.session_state["current_question_idx"] = min(total_items - 1, cur_idx + 1)
            st.rerun()
    else:
        can_finish = all(v is not None for v in st.session_state["assessment_answers"].values())
        if st.button("Selesai & Analisis ✨", type="primary", use_container_width=True, disabled=not can_finish):
            loading_box = st.empty()
            loading_box.markdown(
                render_mental_health_loader("Sedang menyelaraskan dimensi emosional, sosial, dan psikologis..."),
                unsafe_allow_html=True,
            )

            normalized = [
                response_mapping[st.session_state["assessment_answers"][i]]
                for i in range(1, 15)
            ]

            time.sleep(1.2)

            res = assess_student(normalized)
            user_id = st.session_state.get("user", {}).get("id")
            save_assessment(res, user_id=user_id)

            loading_box.empty()
            st.session_state["assessment_result"] = res
            st.rerun()

if not all(v is not None for v in st.session_state["assessment_answers"].values()):
    unanswered_list = [i for i, v in st.session_state["assessment_answers"].items() if v is None]
    st.caption(f"ℹ️ Pertanyaan belum terjawab: {len(unanswered_list)} butir (Nomor: {', '.join(map(str, unanswered_list))})")
