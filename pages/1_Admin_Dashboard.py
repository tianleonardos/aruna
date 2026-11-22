import sys
from pathlib import Path
import json
import sqlite3
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.theme import apply_theme, get_vector, get_logo_base64

# Cek autentikasi dan otorisasi Administrator
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# Terapkan gaya visual & atur visibilitas sidebar
apply_theme(hide_sidebar=not is_admin)

if not is_admin:
    st.warning("⚠️ Akses Terbatas: Halaman ini hanya dapat diakses oleh Administrator.")
    st.info("Silakan login menggunakan akun Administrator di Beranda Utama.")
    st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda Utama", icon="🌱")
    st.stop()

# =========================================================
# PATH CONFIGURATION
# =========================================================

DATABASE_PATH = ROOT_DIR / "database" / "aruna.db"
REGISTRY_PATH = ROOT_DIR / "models" / "registry.json"
ACTIVE_MODEL_PATH = ROOT_DIR / "models" / "active" / "aruna_model_final.joblib"
REFERENCE_DATA_DIR = ROOT_DIR / "data" / "reference"


# =========================================================
# HEADER DENGAN VEKTOR ORGANIK & LOGO RESMI
# =========================================================

logo_data_uri = get_logo_base64()
h_col1, h_col2 = st.columns([3, 1], vertical_alignment="center")

with h_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">Administrator & Peneliti</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Admin Dashboard")
    st.caption("Monitoring aktivitas asesmen mahasiswa, data referensi, dan model Machine Learning Aruna.")

with h_col2:
    st.markdown(
        f'<div style="max-width: 130px; margin: auto;">{get_vector("research_matrix")}</div>',
        unsafe_allow_html=True,
    )

st.divider()


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

@st.cache_data(ttl=30)
def load_assessment_data():
    """Mengambil data agregat dan riwayat asesmen dari SQLite."""
    if not DATABASE_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DATABASE_PATH) as connection:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type = 'table'",
            connection,
        )["name"].tolist()

        if "assessment_history" not in tables:
            return pd.DataFrame()

        data = pd.read_sql_query(
            """
            SELECT
                id,
                unique_code,
                user_id,
                created_at,
                emotional,
                social,
                psychological,
                overall_profile,
                pattern_profile
            FROM assessment_history
            ORDER BY created_at DESC
            """,
            connection,
        )

    return data


def load_model_info():
    """Membaca informasi versi model dari registry."""
    info = {
        "available": ACTIVE_MODEL_PATH.exists(),
        "version": "Belum diketahui",
        "registry_exists": REGISTRY_PATH.exists(),
    }

    if not REGISTRY_PATH.exists():
        return info

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as file:
            registry = json.load(file)

        version = registry.get("active_version")
        if version is not None:
            info["version"] = f"v{version}"
    except (json.JSONDecodeError, OSError):
        pass

    return info


# =========================================================
# LOAD DATA & SUMMARY METRICS
# =========================================================

assessment_data = load_assessment_data()
model_info = load_model_info()

if not assessment_data.empty:
    assessment_data["created_at"] = pd.to_datetime(
        assessment_data["created_at"],
        errors="coerce",
    )
    total_assessments = len(assessment_data)
    latest_assessment = assessment_data["created_at"].max()
    today = pd.Timestamp.now().normalize()
    assessments_today = (
        assessment_data["created_at"].dt.normalize() == today
    ).sum()

    profiles = (
        assessment_data
        .groupby(["overall_profile", "pattern_profile"])
        .size()
        .reset_index(name="Jumlah")
    )
    dimension_means = assessment_data[
        ["emotional", "social", "psychological"]
    ].mean()
else:
    total_assessments = 0
    latest_assessment = None
    assessments_today = 0
    profiles = pd.DataFrame()
    dimension_means = pd.Series(dtype=float)

if REFERENCE_DATA_DIR.exists():
    reference_files = [f for f in REFERENCE_DATA_DIR.iterdir() if f.is_file()]
else:
    reference_files = []
dataset_count = len(reference_files)

st.subheader("Ringkasan Sistem & Operasional")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Asesmen Mahasiswa", f"{total_assessments:,}")
with col2:
    st.metric("Asesmen Hari Ini", f"{assessments_today:,}")
with col3:
    st.metric("Dataset Referensi", f"{dataset_count} File")
with col4:
    st.metric("Model ML Aktif", model_info["version"])

# =========================================================
# QUICK ACTION LINKS
# =========================================================

st.markdown("#### Akses Cepat Modul Administrator")
qa1, qa2, qa3, qa4, qa5 = st.columns(5)

with qa1:
    st.page_link("pages/8_Website_CRUD.py", label="Manajemen Konten (CMS)", icon="✏️", use_container_width=True)
with qa2:
    st.page_link("pages/2_Dataset_Management.py", label="Manajemen Dataset", icon="📁", use_container_width=True)
with qa3:
    st.page_link("pages/3_Model_Training.py", label="Model Training", icon="⚙️", use_container_width=True)
with qa4:
    st.page_link("pages/4_Model_Evaluation.py", label="Evaluasi Model", icon="📈", use_container_width=True)
with qa5:
    st.page_link("pages/5_Model_Registry.py", label="Model Registry", icon="🗃️", use_container_width=True)


# =========================================================
# SYSTEM STATUS
# =========================================================

st.divider()
st.subheader("Status Komponen Sistem")

status_col1, status_col2, status_col3 = st.columns(3)
with status_col1:
    if DATABASE_PATH.exists():
        st.success("Database SQLite Aktif")
    else:
        st.warning("Database SQLite Belum Dibuat")

with status_col2:
    if model_info["available"]:
        st.success("Artefak Model Aktif Tersedia (.joblib)")
    else:
        st.error("Artefak Model Aktif Tidak Ditemukan")

with status_col3:
    if model_info["registry_exists"]:
        st.success("Model Registry Terdaftar")
    else:
        st.warning("Model Registry Belum Dibuat")


# =========================================================
# ASSESSMENT ANALYTICS
# =========================================================

st.divider()
st.subheader("Analisis Hasil Asesmen Mahasiswa")

if assessment_data.empty:
    st.info(
        "Belum terdapat data asesmen yang masuk. "
        "Ringkasan analitik dan grafik akan muncul otomatis setelah mahasiswa menyelesaikan asesmen."
    )
else:
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("**Distribusi Profil Mahasiswa Terdaftar**")
        if not profiles.empty:
            profiles["Profil"] = profiles["overall_profile"] + " - " + profiles["pattern_profile"]
            profile_chart = profiles.set_index("Profil")[["Jumlah"]]
            st.bar_chart(profile_chart)
        else:
            st.info("Belum ada data profil.")

    with right_col:
        st.markdown("**Rata-rata Skor Tiga Dimensi**")
        dimension_display = dimension_means.rename({
            "emotional": "Emosional",
            "social": "Sosial",
            "psychological": "Psikologis",
        })
        st.bar_chart(dimension_display)


# =========================================================
# RECENT ACTIVITY & REFERENCE DATASET
# =========================================================

st.divider()
rec_col, ref_col = st.columns(2)

with rec_col:
    st.subheader("Aktivitas Asesmen Terbaru")
    if assessment_data.empty:
        st.caption("Belum ada riwayat aktivitas.")
    else:
        latest_data = assessment_data.head(5).copy()
        latest_data["Waktu"] = latest_data["created_at"].dt.strftime("%d-%m-%Y %H:%M")
        latest_data["Profil"] = latest_data["overall_profile"] + " - " + latest_data["pattern_profile"]
        latest_data["Kode Asesmen"] = latest_data["unique_code"].fillna(latest_data["id"].apply(lambda x: f"ARN-{x}"))
        st.dataframe(
            latest_data[["Kode Asesmen", "Waktu", "Profil"]],
            use_container_width=True,
            hide_index=True,
        )

with ref_col:
    st.subheader("Dataset Referensi Penelitian")
    if reference_files:
        dataset_table = pd.DataFrame([
            {
                "Nama File": f.name,
                "Ukuran (KB)": round(f.stat().st_size / 1024, 2),
                "Format": f.suffix.upper(),
            }
            for f in reference_files
        ])
        st.dataframe(dataset_table, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada file di folder data/reference.")

# =========================================================
# AUDIT LOG LENGKAP KODE ASESMEN MAHASISWA
# =========================================================

st.divider()
st.subheader("📋 Audit Log & Riwayat Kode Unik Seluruh Asesmen")
st.caption("Khusus administrator: verifikasi riwayat pengerjaan mahasiswa dengan kode unik terenkripsi untuk audit etis.")

if assessment_data.empty:
    st.info("Belum ada data riwayat asesmen yang tersimpan untuk diaudit.")
else:
    search_q = st.text_input("🔍 Cari Kode Asesmen atau Profil:", placeholder="Contoh: ARN-2026 atau Rendah...")

    audit_df = assessment_data.copy()
    audit_df["Kode Asesmen"] = audit_df["unique_code"].fillna(audit_df["id"].apply(lambda x: f"ARN-{x}"))
    audit_df["Waktu Selesai"] = audit_df["created_at"].dt.strftime("%d-%m-%Y %H:%M")
    audit_df["Profil"] = audit_df["overall_profile"] + " - " + audit_df["pattern_profile"]
    audit_df["Emosional"] = audit_df["emotional"].round(2)
    audit_df["Sosial"] = audit_df["social"].round(2)
    audit_df["Psikologis"] = audit_df["psychological"].round(2)

    if search_q.strip():
        mask = (
            audit_df["Kode Asesmen"].str.contains(search_q, case=False, na=False)
            | audit_df["Profil"].str.contains(search_q, case=False, na=False)
        )
        audit_df = audit_df[mask]

    cols_to_show = ["Kode Asesmen", "Waktu Selesai", "Profil", "Emosional", "Sosial", "Psikologis"]
    st.dataframe(audit_df[cols_to_show], use_container_width=True, hide_index=True)

    csv_data = audit_df[cols_to_show].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Unduh Rekap Audit Kode Asesmen (CSV)",
        data=csv_data,
        file_name="audit_riwayat_asesmen_aruna.csv",
        mime="text/csv",
    )
