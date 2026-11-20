
from pathlib import Path
import json
import sqlite3

import pandas as pd
import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# =========================================================
# PATH CONFIGURATION
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

DATABASE_PATH = ROOT_DIR / "database" / "aruna.db"
REGISTRY_PATH = ROOT_DIR / "models" / "registry.json"
ACTIVE_MODEL_PATH = ROOT_DIR / "models" / "active" / "aruna_model_final.joblib"

REFERENCE_DATA_DIR = ROOT_DIR / "data" / "reference"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Admin Dashboard | Aruna",
    page_icon="📊",
    layout="wide",
)

st.title("Admin Dashboard")
st.caption(
    "Ringkasan aktivitas asesmen, dataset referensi, "
    "dan model Machine Learning Aruna."
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
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """,
            connection,
        )["name"].tolist()

        if "assessment_history" not in tables:
            return pd.DataFrame()

        data = pd.read_sql_query(
            """
            SELECT
                id,
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


# =========================================================
# MODEL REGISTRY INFORMATION
# =========================================================

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

        def find_version(data):
            if isinstance(data, dict):
                for key in (
                    "active_version",
                    "current_version",
                    "active_model_version",
                ):
                    if key in data:
                        return data[key]

                for value in data.values():
                    result = find_version(value)
                    if result is not None:
                        return result

            elif isinstance(data, list):
                for value in data:
                    result = find_version(value)
                    if result is not None:
                        return result

            return None

        version = find_version(registry)

        if version is not None:
            info["version"] = str(version)

    except (json.JSONDecodeError, OSError):
        pass

    return info


# =========================================================
# LOAD DATA
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


# =========================================================
# DATASET INFORMATION
# =========================================================

if REFERENCE_DATA_DIR.exists():
    reference_files = [
        file for file in REFERENCE_DATA_DIR.iterdir()
        if file.is_file()
    ]
else:
    reference_files = []

dataset_count = len(reference_files)


# =========================================================
# SUMMARY METRICS
# =========================================================

st.subheader("Ringkasan Sistem")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Asesmen",
        f"{total_assessments:,}",
    )

with col2:
    st.metric(
        "Asesmen Hari Ini",
        f"{assessments_today:,}",
    )

with col3:
    st.metric(
        "Dataset Referensi",
        dataset_count,
    )

with col4:
    st.metric(
        "Model Aktif",
        model_info["version"],
    )


# =========================================================
# SYSTEM STATUS
# =========================================================

st.divider()
st.subheader("Status Sistem")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    if DATABASE_PATH.exists():
        st.success("Database tersedia")
    else:
        st.warning("Database belum tersedia")

with status_col2:
    if model_info["available"]:
        st.success("Artefak model tersedia")
    else:
        st.error("Artefak model tidak ditemukan")

with status_col3:
    if model_info["registry_exists"]:
        st.success("Model registry tersedia")
    else:
        st.warning("Registry belum tersedia")


# =========================================================
# ASSESSMENT ANALYTICS
# =========================================================

st.divider()
st.subheader("Analisis Aktivitas Asesmen")

if assessment_data.empty:

    st.info(
        "Belum terdapat data asesmen. "
        "Ringkasan analisis akan muncul setelah mahasiswa "
        "menyelesaikan asesmen MHC-SF."
    )

else:

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("**Distribusi Profil Mahasiswa**")

        if not profiles.empty:
            profiles["Profil"] = (
                profiles["overall_profile"]
                + " + "
                + profiles["pattern_profile"]
            )

            profile_chart = profiles.set_index("Profil")[["Jumlah"]]

            st.bar_chart(profile_chart)

        else:
            st.info("Belum ada distribusi profil.")

    with right_col:
        st.markdown("**Rata-rata Skor Dimensi**")

        dimension_display = dimension_means.rename({
            "emotional": "Emosional",
            "social": "Sosial",
            "psychological": "Psikologis",
        })

        st.bar_chart(dimension_display)

        st.caption(
            "Skor merupakan rata-rata hasil asesmen yang tersimpan "
            "pada database prototipe."
        )


# =========================================================
# RECENT ACTIVITY
# =========================================================

st.divider()
st.subheader("Aktivitas Terbaru")

if assessment_data.empty:

    st.info("Belum ada aktivitas asesmen.")

else:

    latest_data = assessment_data.head(5).copy()

    latest_data["created_at"] = (
        latest_data["created_at"]
        .dt.strftime("%d-%m-%Y %H:%M")
    )

    latest_data = latest_data.rename(columns={
        "created_at": "Waktu",
        "overall_profile": "Profil Keseluruhan",
        "pattern_profile": "Pola Dimensi",
    })

    st.dataframe(
        latest_data[
            [
                "Waktu",
                "Profil Keseluruhan",
                "Pola Dimensi",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    if latest_assessment is not None:
        st.caption(
            "Asesmen terbaru tercatat pada "
            + latest_assessment.strftime("%d %B %Y, %H:%M")
        )


# =========================================================
# REFERENCE DATASET
# =========================================================

st.divider()
st.subheader("Dataset Referensi")

if reference_files:

    dataset_table = pd.DataFrame([
        {
            "Nama File": file.name,
            "Ukuran (KB)": round(file.stat().st_size / 1024, 2),
            "Format": file.suffix.upper(),
        }
        for file in reference_files
    ])

    st.dataframe(
        dataset_table,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "Belum ditemukan file pada direktori data/reference."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Aruna Admin Dashboard | Mental Well-Being Profile Mapping "
    "with Unsupervised Machine Learning"
)

st.caption(
    "Informasi yang ditampilkan merupakan ringkasan data prototipe, "
    "bukan hasil diagnosis atau penilaian klinis."
)
