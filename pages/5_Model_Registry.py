import sys
from pathlib import Path
import shutil
import joblib

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from src.theme import apply_theme, get_vector, get_logo_base64
from src.model_registry import (
    initialize_registry,
    load_registry,
    save_registry,
    get_model_history,
    get_active_model_info,
)

# Cek autentikasi dan peran admin
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# Terapkan styling & kontrol visibilitas sidebar
apply_theme(hide_sidebar=not is_admin)

if not is_admin:
    st.warning("⚠️ Akses Terbatas: Halaman ini hanya dapat diakses oleh Administrator & Peneliti.")
    st.info("Silakan login menggunakan akun Administrator di Beranda Utama.")
    st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda Utama", icon="🌱")
    st.stop()

# Tombol navigasi kembali ke Admin Dashboard
st.page_link("pages/1_Admin_Dashboard.py", label="⬅️ Kembali ke Admin Dashboard", icon="🏠")

logo_data_uri = get_logo_base64()
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
        <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
        <div>
            <span class="aruna-badge">Siklus Hidup Model ML</span>
            <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("Model Registry & Versi")
st.caption("Kelola siklus hidup, audit metadata, dan promosi versi model aktif Aruna.")
st.divider()

# Pastikan registry sudah diinisialisasi
try:
    initialize_registry()
except Exception as e:
    st.error(f"Gagal memuat registry: {e}")
    st.stop()

registry = load_registry()
active_version = registry.get("active_version", "1.0")
active_model_path = ROOT_DIR / "models" / "active" / "aruna_model_final.joblib"
versions_dir = ROOT_DIR / "models" / "versions"


# ===========================================================================
# 1. STATUS MODEL AKTIF
# ===========================================================================

st.subheader("1. Model yang Sedang Digunakan (Active Model)")

if not active_model_path.exists():
    st.warning("File model aktif belum ditemukan di models/active/aruna_model_final.joblib.")
else:
    try:
        active_package = joblib.load(active_model_path)
        training_info = active_package.get("training_info", {})

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Versi Aktif", f"v{active_version}")
        col_m2.metric("Arsitektur", training_info.get("architecture", "Two-Layer K-Means"))
        col_m3.metric("Data Latih", f"{training_info.get('dataset_size', 332)} Sampel")
        col_m4.metric("Jumlah Profil", "4 Kombinasi")

        with st.expander("Lihat Detail Konfigurasi & Ambang Batas Model Aktif"):
            st.markdown(f"**Waktu Pembuatan:** `{active_package.get('created_at', 'N/A')}`")
            st.markdown(f"**Pemetaan Overall:** `{active_package.get('overall_label_map')}`")
            st.markdown(f"**Pemetaan Pattern:** `{active_package.get('pattern_label_map')}`")
            st.markdown(f"**Ambang Kuartil Q1:** `{active_package.get('q1_thresholds')}`")
            st.markdown(f"**Urutan Fitur:** `{active_package.get('feature_columns')}`")

    except Exception as ex:
        st.error(f"Gagal membaca paket model aktif: {ex}")


# ===========================================================================
# 2. RIWAYAT DAFTAR MODEL TERDAFTAR
# ===========================================================================

st.divider()
st.subheader("2. Riwayat Versi Model Terdaftar")

models_list = registry.get("models", [])
if not models_list:
    st.info("Belum ada riwayat model di dalam registry.")
else:
    table_data = []
    for m in models_list:
        is_active = (str(m.get("version")) == str(active_version))
        table_data.append({
            "Versi": f"v{m.get('version')}",
            "Status": "🟢 Aktif" if is_active else "⚪ Arsip",
            "Nama File": m.get("filename"),
            "Tanggal Registrasi": m.get("registered_at"),
            "Dataset Sumber": m.get("dataset", "thesis data set.xlsx"),
            "Catatan": m.get("notes", "-"),
        })

    st.dataframe(pd.DataFrame(table_data), use_container_width=True)


# ===========================================================================
# 3. PROMOSI & AKTIVASI VERSI MODEL
# ===========================================================================

st.divider()
st.subheader("3. Ganti / Promosikan Model Aktif")

candidate_versions = [
    m for m in models_list
    if str(m.get("version")) != str(active_version)
]

if not candidate_versions:
    st.info("Hanya ada 1 versi model yang terdaftar saat ini. Belum ada model alternatif untuk diaktifkan.")
else:
    version_options = {
        f"Versi v{m['version']} ({m['filename']}) - {m.get('registered_at', '')}": m
        for m in candidate_versions
    }

    selected_cand_label = st.selectbox(
        "Pilih versi model arsip yang ingin dipromosikan menjadi aktif:",
        options=list(version_options.keys()),
    )

    if st.button("Jadikan Versi Ini sebagai Model Aktif", type="primary"):
        selected_cand = version_options[selected_cand_label]
        target_version = str(selected_cand["version"])
        source_joblib = versions_dir / selected_cand["filename"]

        if not source_joblib.exists():
            st.error(f"File model tidak ditemukan di: {source_joblib}")
        else:
            try:
                # Salin file ke active model
                shutil.copy2(source_joblib, active_model_path)

                # Update registry json
                for m in registry["models"]:
                    if str(m.get("version")) == target_version:
                        m["status"] = "active"
                    else:
                        m["status"] = "archived"

                registry["active_version"] = target_version
                save_registry(registry)

                st.success(f"Berhasil! Model v{target_version} sekarang aktif digunakan.")
                st.rerun()

            except Exception as e:
                st.error(f"Gagal mempromosikan model: {e}")


# ===========================================================================
# 4. UNDUH ARTEFAK MODEL AKTIF
# ===========================================================================

st.divider()
st.subheader("4. Unduh Artefak Model")
st.caption("Unduh paket model Joblib untuk keperluan backup lokal, pengujian eksternal, atau audit penelitian.")

if active_model_path.exists():
    with open(active_model_path, "rb") as f:
        model_bytes = f.read()

    st.download_button(
        label=f"📥 Unduh aruna_model_final.joblib (v{active_version})",
        data=model_bytes,
        file_name="aruna_model_final.joblib",
        mime="application/octet-stream",
    )
