"""Halaman Model Training ARUNA (Otomatis & Terintegrasi).

Menyediakan proses pelatihan model satu tombol (One-Click Automated Training)
tanpa konfigurasi parameter rumit. Menampilkan animasi loading 3 dimensi
bertema kesehatan mental saat proses berlangsung.
"""

from __future__ import annotations
import sys
import time
from pathlib import Path
from datetime import datetime
import shutil
import joblib

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np

from src.theme import apply_theme, get_vector, render_mental_health_loader, get_logo_base64
from src.preprocessing import preprocess_mhcsf_dataset
from src.clustering import (
    train_two_layer_model,
    run_model_selection,
    FEATURE_COLUMNS,
)
from src.model_registry import load_registry, save_registry, initialize_registry

# Cek autentikasi dan peran admin
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# Terapkan styling responsif & kontrol visibilitas sidebar
apply_theme(hide_sidebar=not is_admin)

if not is_admin:
    st.warning("⚠️ Akses Terbatas: Halaman ini hanya dapat diakses oleh Administrator & Peneliti.")
    st.info("Silakan login menggunakan akun Administrator di Beranda Utama.")
    st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda Utama", icon="🌱")
    st.stop()

# Tombol navigasi kembali ke Admin Dashboard
st.page_link("pages/1_Admin_Dashboard.py", label="⬅️ Kembali ke Admin Dashboard", icon="🏠")

initialize_database_check = initialize_registry()

# ===========================================================================
# HEADER MODEL TRAINING
# ===========================================================================

logo_data_uri = get_logo_base64()
h_col1, h_col2 = st.columns([3, 1], vertical_alignment="center")

with h_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">Machine Learning Engine</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Model Training")
    st.caption("Pelatihan otomatis model pemetaan kesejahteraan mental berbasis Unsupervised Learning.")

with h_col2:
    st.markdown(f'<div style="max-width: 120px; margin: auto;">{get_vector("research_matrix")}</div>', unsafe_allow_html=True)

st.divider()


# ===========================================================================
# 1. SUMBER DATASET PELATIHAN
# ===========================================================================

st.subheader("1. Sumber Dataset")

ref_path = ROOT_DIR / "data" / "reference" / "thesis data set.xlsx"
uploaded_dir = ROOT_DIR / "data" / "uploaded"

available_datasets = {}
if ref_path.exists():
    available_datasets["Dataset Referensi Penelitian (thesis data set.xlsx)"] = ref_path

if uploaded_dir.exists():
    for f in uploaded_dir.glob("*.xlsx"):
        available_datasets[f"Dataset Unggahan: {f.name}"] = f
    for f in uploaded_dir.glob("*.csv"):
        available_datasets[f"Dataset Unggahan: {f.name}"] = f

if not available_datasets:
    st.error("Tidak ada dataset yang ditemukan di folder data/reference atau data/uploaded.")
    st.stop()

selected_dataset_label = st.selectbox(
    "Pilih dataset untuk melatih model:",
    options=list(available_datasets.keys()),
)
selected_file_path = available_datasets[selected_dataset_label]


# ===========================================================================
# 2. PELATIHAN SATU TOMBOL (ONE-CLICK AUTOMATED TRAINING)
# ===========================================================================

st.divider()
st.subheader("2. Eksekusi Pelatihan Otomatis")
st.write(
    "Sistem akan secara otomatis memvalidasi data mahasiswa, melakukan pembersihan "
    "dan standardisasi ordinal, menghitung skor dimensi, serta mengoptimasi model clustering terbaik."
)

start_train = st.button("🚀 Mulai Model Training Otomatis", type="primary", use_container_width=True)

if start_train:
    # Container animasi loading mental health 3D
    loading_placeholder = st.empty()
    loading_placeholder.markdown(
        render_mental_health_loader("Sedang menyelaraskan dimensi emosional, sosial, dan psikologis..."),
        unsafe_allow_html=True,
    )

    try:
        # 1. Muat dataset
        if selected_file_path.suffix.lower() == ".xlsx":
            raw_df = pd.read_excel(selected_file_path)
        else:
            raw_df = pd.read_csv(selected_file_path)

        # 2. Preprocessing data
        prep = preprocess_mhcsf_dataset(raw_df)
        clean_data_3 = prep["features_3"]

        # Jeda visual agar animasi harmoni 3D terasa menenangkan
        time.sleep(1.2)

        # 3. Training model
        training_res = train_two_layer_model(clean_data_3)
        package = training_res["model_package"]

        # 4. Generate versi baru otomatis
        reg_data = load_registry()
        active_ver = reg_data.get("active_version", "1.0")
        try:
            new_ver_num = round(float(active_ver) + 0.1, 1)
            new_version_str = f"{new_ver_num:.1f}"
        except ValueError:
            new_version_str = f"1.{len(reg_data.get('models', [])) + 1}"

        package["model_version"] = new_version_str
        package["created_at"] = datetime.now().isoformat()

        # Simpan ke versions
        versions_dir = ROOT_DIR / "models" / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)
        version_filename = f"aruna_model_v{new_version_str}.joblib"
        target_version_path = versions_dir / version_filename
        joblib.dump(package, target_version_path)

        # Tetapkan sebagai model aktif
        active_path = ROOT_DIR / "models" / "active" / "aruna_model_final.joblib"
        shutil.copy2(target_version_path, active_path)

        # Update registry
        for m in reg_data.get("models", []):
            m["status"] = "archived"

        reg_data["active_version"] = new_version_str
        reg_data.setdefault("models", []).append({
            "version": new_version_str,
            "filename": version_filename,
            "status": "active",
            "registered_at": datetime.now().isoformat(timespec="seconds"),
            "dataset": selected_file_path.name,
            "dataset_size": len(clean_data_3),
            "notes": "Model training otomatis one-click.",
        })
        save_registry(reg_data)

        # Bersihkan animasi loading
        loading_placeholder.empty()

        # Tampilkan ringkasan sukses
        st.success(f"🎉 Model Training Berhasil! Model versi v{new_version_str} telah aktif digunakan.")

        st.session_state["recent_training"] = {
            "version": new_version_str,
            "samples": len(clean_data_3),
            "overall_map": package["overall_label_map"],
            "pattern_map": package["pattern_label_map"],
            "q1": package["q1_thresholds"],
            "labels_overall": training_res["overall_labels"],
            "labels_pattern": training_res["pattern_labels"],
        }

    except Exception as err:
        loading_placeholder.empty()
        st.error(f"Gagal melakukan pelatihan model: {err}")
        st.exception(err)


# ===========================================================================
# 3. HASIL EVALUASI MODEL TERBARU
# ===========================================================================

recent = st.session_state.get("recent_training")

if recent:
    st.divider()
    st.subheader(f"Ringkasan Model Aktif (Versi v{recent['version']})")

    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Status Model", "🟢 Aktif & Siap Pakai")
    col_res2.metric("Ukuran Data Latih", f"{recent['samples']} Responden")
    col_res3.metric("Pemetaan Kesejahteraan", "4 Profil Interpretatif")

    # Distribusi profil
    o_map = recent["overall_map"]
    p_map = recent["pattern_map"]
    comb = [f"{o_map[o]} - {p_map[p]}" for o, p in zip(recent["labels_overall"], recent["labels_pattern"])]
    dist_s = pd.Series(comb).value_counts().reset_index()
    dist_s.columns = ["Profil Kesejahteraan", "Jumlah Mahasiswa"]
    dist_s["Proporsi (%)"] = (dist_s["Jumlah Mahasiswa"] / len(comb)) * 100

    st.markdown("**Distribusi Profil Mahasiswa Terbentuk:**")
    st.dataframe(dist_s, use_container_width=True)

    st.page_link("pages/4_Model_Evaluation.py", label="Lihat Analisis Evaluasi Lengkap ➡️", icon="📈")
