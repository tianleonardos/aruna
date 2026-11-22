
from pathlib import Path
from datetime import datetime
import re
import unicodedata
import sys

import pandas as pd
import streamlit as st


# =========================================================
# 1. PROJECT CONFIGURATION
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.preprocessing import (
    detect_mhcsf_columns,
    detect_status_column,
    get_invalid_response_values,
    RESPONSE_MAPPING,
    MISSING_RESPONSES,
)

DATA_UPLOADED_DIR = ROOT_DIR / "data" / "uploaded"
DATA_REFERENCE_DIR = ROOT_DIR / "data" / "reference"

DATA_UPLOADED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATA_REFERENCE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


from src.theme import apply_theme, get_vector, get_logo_base64

# Cek autentikasi dan peran admin
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# Atur visibilitas sidebar: hanya admin yang memiliki sidebar
apply_theme(hide_sidebar=not is_admin)

if not is_admin:
    st.warning("⚠️ Akses Terbatas: Halaman ini hanya dapat diakses oleh Administrator & Peneliti.")
    st.info("Silakan login menggunakan akun Administrator di Beranda Utama.")
    st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda Utama", icon="🌱")
    st.stop()

# Tombol navigasi kembali ke Admin Dashboard
st.page_link("pages/1_Admin_Dashboard.py", label="⬅️ Kembali ke Admin Dashboard", icon="🏠")

# =========================================================
# 2. PAGE CONFIGURATION
# =========================================================

logo_data_uri = get_logo_base64()
h_col1, h_col2 = st.columns([3, 1], vertical_alignment="center")

with h_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">Manajemen Data</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Dataset Management")
    st.caption(
        "Kelola, periksa kelengkapan, validasi format MHC-SF, "
        "dan simpan dataset untuk eksperimen model Aruna."
    )

with h_col2:
    st.markdown(
        f'<div style="max-width: 120px; margin: auto;">{get_vector("research_matrix")}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# DATASET OVERVIEW
# =========================================================

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

reference_files = [
    file for file in DATA_REFERENCE_DIR.iterdir()
    if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
]

uploaded_files = [
    file for file in DATA_UPLOADED_DIR.iterdir()
    if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
]

total_datasets = len(reference_files) + len(uploaded_files)

st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Dataset", total_datasets)

with col2:
    st.metric("Dataset Referensi", len(reference_files))

with col3:
    st.metric("Dataset Upload", len(uploaded_files))

with st.expander("Lihat Dataset Tersimpan"):
    if total_datasets == 0:
        st.info("Belum ada dataset yang tersimpan.")
    else:
        dataset_inventory = []

        for file in reference_files:
            dataset_inventory.append({
                "Nama Dataset": file.name,
                "Kategori": "Referensi",
                "Lokasi": "data/reference/"
            })

        for file in uploaded_files:
            dataset_inventory.append({
                "Nama Dataset": file.name,
                "Kategori": "Uploaded",
                "Lokasi": "data/uploaded/"
            })

        st.dataframe(
            pd.DataFrame(dataset_inventory),
            use_container_width=True,
            hide_index=True
        )

st.divider()

# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def normalize_value(value):
    if pd.isna(value):
        return None

    value = unicodedata.normalize("NFKC", str(value))
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip().casefold()

def normalize_header(column):
    """
    Menyeragamkan nama kolom agar tidak berbeda
    akibat spasi atau karakter tersembunyi.
    """
    column = str(column)

    # Normalisasi karakter Unicode
    column = unicodedata.normalize("NFKC", column)

    # Mengganti karakter spasi khusus
    column = column.replace("\u00a0", " ")

    # Menghapus zero-width characters
    column = column.replace("\u200b", "")

    # Merapikan spasi berulang
    column = re.sub(r"\s+", " ", column)

    return column.strip()

def read_uploaded_dataset(uploaded_file):
    """
    Membaca file CSV atau Excel yang diunggah.
    """

    file_name = uploaded_file.name.lower()

    try:

        if file_name.endswith(".csv"):

            try:

                return pd.read_csv(
                    uploaded_file,
                    encoding="utf-8-sig"
                )

            except UnicodeDecodeError:

                uploaded_file.seek(0)

                return pd.read_csv(
                    uploaded_file,
                    encoding="latin-1"
                )

        elif file_name.endswith((".xlsx", ".xls")):

            return pd.read_excel(uploaded_file)

        else:

            raise ValueError(
                "Format file tidak didukung. "
                "Gunakan CSV atau Excel."
            )

    except Exception as error:

        raise ValueError(
            f"Gagal membaca dataset: {error}"
        ) from error

def validate_response_categories(data, mhcsf_columns):
    return get_invalid_response_values(
        data,
        mhcsf_columns
    )

def inspect_dataset(data):
    total_rows = len(data)
    total_columns = len(data.columns)

    # Missing value teknis pada seluruh dataset
    missing_per_column = data.isna().sum()
    total_missing = int(missing_per_column.sum())

    duplicate_rows = int(data.duplicated().sum())

    # Deteksi struktur MHC-SF dan kolom status mahasiswa
    mhcsf_columns = detect_mhcsf_columns(data)
    status_column = detect_status_column(data)

    mhcsf_valid = len(mhcsf_columns) == 14

    # Filter responden berdasarkan status mahasiswa aktif
    if status_column is not None:
        status_mask = (
            data[status_column]
            .apply(normalize_value)
            .eq(normalize_value("Yes"))
        )

        active_df = data.loc[status_mask].copy()
        active_source_rows = [
            i + 2
            for i, is_active in enumerate(status_mask.to_numpy())
            if is_active
        ]

        active_students = len(active_df)
        excluded_non_active = total_rows - active_students
    else:
        active_df = data.copy()
        active_source_rows = list(range(2, total_rows + 2))

        active_students = None
        excluded_non_active = None

    # Nilai default jika struktur MHC-SF tidak valid
    mhcsf_missing_per_column = pd.Series(dtype="int64")
    mhcsf_missing_total = None
    complete_rows = None
    incomplete_rows = None
    completeness_distribution = pd.DataFrame()
    incomplete_details = pd.DataFrame()
    invalid_results = {}

    if mhcsf_valid:
        missing_categories = {
            normalize_value(value)
            for value in MISSING_RESPONSES
        }

        # Deteksi missing secara semantik:
        # termasuk "Prefer not to answer", bukan hanya NaN
        mhcsf_data = active_df[mhcsf_columns]

        mhcsf_missing_mask = mhcsf_data.apply(
            lambda column: (
                column.isna()
                | column.apply(normalize_value).isin(missing_categories)
            )
        )

        # Missing per butir MHC-SF
        mhcsf_missing_per_column = (
            mhcsf_missing_mask.sum()
            .astype(int)
        )

        mhcsf_missing_total = int(
            mhcsf_missing_per_column.sum()
        )

        # Jumlah butir kosong pada setiap responden
        missing_count = mhcsf_missing_mask.sum(axis=1)

        complete_mask = missing_count.eq(0)
        incomplete_mask = missing_count.gt(0)

        complete_rows = int(complete_mask.sum())
        incomplete_rows = int(incomplete_mask.sum())

        # Distribusi jumlah respons kosong per responden

        completeness_distribution = (
            missing_count.value_counts()
            .sort_index()
            .rename_axis("Jumlah Butir Kosong")
            .reset_index(name="Jumlah Responden")
        )

        completeness_distribution["Persentase (%)"] = (
            completeness_distribution["Jumlah Responden"]
            / len(active_df) * 100
        ).round(2)


        # Detail responden tidak lengkap.
        # Menggunakan nomor baris file, bukan identitas pribadi.
        incomplete_positions = [
            i
            for i, is_incomplete in enumerate(incomplete_mask.to_numpy())
            if is_incomplete
        ]

        incomplete_details = pd.DataFrame({
            "Nomor Baris (di File)": [
                active_source_rows[i]
                for i in incomplete_positions
            ],
            "Jumlah Respons Kosong": [
                int(missing_count.iloc[i])
                for i in incomplete_positions
            ],
            "Butir Tidak Lengkap": [
                ", ".join(
                    mhcsf_columns[j]
                    for j, is_missing in enumerate(
                        mhcsf_missing_mask.iloc[i].to_numpy()
                    )
                    if is_missing
                )
                for i in incomplete_positions
            ]
        })

        # Validasi kategori jawaban pada responden yang masuk
        # ke populasi analisis
        invalid_results = validate_response_categories(
            active_df,
            mhcsf_columns
        )

    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "total_missing": total_missing,
        "missing_per_column": missing_per_column,
        "duplicate_rows": duplicate_rows,

        "mhcsf_columns": mhcsf_columns,
        "status_column": status_column,
        "mhcsf_valid": mhcsf_valid,

        "active_students": active_students,
        "excluded_non_active": excluded_non_active,

        "mhcsf_missing_total": mhcsf_missing_total,
        "mhcsf_missing_per_column": mhcsf_missing_per_column,

        "complete_rows": complete_rows,
        "incomplete_rows": incomplete_rows,
        "completeness_distribution": completeness_distribution,
        "incomplete_details": incomplete_details,

        "invalid_results": invalid_results
    }


def save_uploaded_dataset(data, original_filename):
    """
    Menyimpan dataset mentah ke data/uploaded.

    File tidak akan menimpa dataset referensi.
    """

    original_path = Path(original_filename)

    extension = original_path.suffix.lower()

    if extension not in [".csv", ".xlsx", ".xls"]:
        raise ValueError("Ekstensi file tidak didukung.")

    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        original_path.stem
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_name = (
        f"{safe_name}_{timestamp}{extension}"
    )

    output_path = DATA_UPLOADED_DIR / output_name

    if extension == ".csv":

        data.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

    else:

        data.to_excel(
            output_path,
            index=False
        )

    return output_path


# =========================================================
# 4. UPLOAD DATASET
# =========================================================

st.subheader("Upload Dataset")

uploaded_file = st.file_uploader(
    "Pilih dataset yang ingin diperiksa",
    type=["csv", "xlsx", "xls"],
    help="Format yang didukung: CSV dan Excel."
)


# =========================================================
# 5. LOAD DATASET
# =========================================================

if uploaded_file is not None:

    try:

        data = read_uploaded_dataset(uploaded_file)

        if data.empty:

            st.error(
                "Dataset tidak memiliki baris data."
            )

            st.stop()

        # Simpan dataset dalam session state.
        st.session_state["dataset_upload"] = data

        st.session_state["dataset_filename"] = (
            uploaded_file.name
        )

    except Exception as error:

        st.error(str(error))

        st.stop()


# =========================================================
# 6. DISPLAY DATASET
# =========================================================

if "dataset_upload" in st.session_state:

    data = st.session_state["dataset_upload"]

    filename = st.session_state.get(
        "dataset_filename",
        "Dataset"
    )

    st.divider()

    st.subheader("Dataset Preview")

    st.caption(
        f"Nama file: {filename}"
    )

    st.dataframe(
        data.head(10),
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # DATASET METRICS
    # -----------------------------------------------------

    inspection = inspect_dataset(data)

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Baris",
            f"{inspection['total_rows']:,}"
        )

    with col2:

        st.metric(
            "Total Kolom",
            f"{inspection['total_columns']:,}"
        )

    with col3:

        st.metric(
            "Missing Values",
            f"{inspection['total_missing']:,}"
        )

    with col4:

        st.metric(
            "Duplikasi",
            f"{inspection['duplicate_rows']:,}"
        )

    st.divider()

    # =====================================================
    # 7. MHC-SF DETECTION
    # =====================================================

    st.subheader("MHC-SF Column Detection")

    detected_columns = inspection["mhcsf_columns"]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Kolom MHC-SF Terdeteksi",
            f"{len(detected_columns)}/14"
        )

    with col2:

        if inspection["status_column"] is not None:

            st.metric(
                "Kolom Status Mahasiswa",
                "Ditemukan"
            )

        else:

            st.metric(
                "Kolom Status Mahasiswa",
                "Tidak ditemukan"
            )

    if inspection["mhcsf_valid"]:

        st.success(
            "14 butir pertanyaan MHC-SF berhasil terdeteksi."
        )

        with st.expander(
            "Lihat 14 kolom MHC-SF"
        ):

            for index, column in enumerate(
                detected_columns,
                start=1
            ):

                st.write(
                    f"{index}. {column}"
                )

    else:

        st.warning(
            f"Hanya ditemukan {len(detected_columns)} "
            "dari 14 kolom pertanyaan MHC-SF."
        )

        st.info(
            "Deteksi menggunakan awalan pertanyaan MHC-SF "
            "bahasa Inggris atau Indonesia. Periksa nama "
            "header jika kolom belum terdeteksi."
        )

        if detected_columns:

            with st.expander(
                "Lihat kolom yang berhasil terdeteksi"
            ):

                for column in detected_columns:

                    st.write(column)

    # =====================================================
    # 8. STATUS COLUMN INFORMATION
    # =====================================================

    st.divider()

    st.subheader("Student Status Validation")

    if inspection["status_column"] is not None:

        status_column = inspection["status_column"]

        st.success(
            f"Kolom status ditemukan: {status_column}"
        )

        status_distribution = (
            data[status_column]
            .fillna("Missing")
            .astype(str)
            .value_counts()
            .reset_index()
        )

        status_distribution.columns = [
            "Status",
            "Jumlah"
        ]

        st.dataframe(
            status_distribution,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "Kolom status mahasiswa tidak ditemukan. "
            "Dataset ini tidak dapat menjalani seleksi "
            "mahasiswa aktif secara otomatis."
        )

    # =====================================================
    # 9. RESPONSE CATEGORY VALIDATION
    # =====================================================

    st.divider()

    st.subheader("Response Category Validation")

    if not inspection["mhcsf_valid"]:

        st.warning(
            "Validasi kategori belum dijalankan karena "
            "jumlah kolom MHC-SF belum tepat 14."
        )

    elif not inspection["invalid_results"]:

        st.success(
            "Tidak ditemukan kategori respons yang tidak dikenal."
        )

    
    else:
        st.error(
            "Ditemukan kategori respons yang belum dikenali."
        )

        invalid_table = []

        for column, invalid_values in inspection["invalid_results"].items():
            invalid_table.append({
                "Kolom": column,
                "Kategori Tidak Valid": ", ".join(
                    str(value) for value in invalid_values
                ),
            })

        st.dataframe(
            pd.DataFrame(invalid_table),
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # 10. MISSING VALUE ANALYSIS
    # =====================================================

    st.divider()

    st.subheader("MHC-SF Missing Value Analysis")

    if inspection["mhcsf_valid"]:
        st.metric(
            "Total Missing Respons MHC-SF",
            inspection["mhcsf_missing_total"]
        )

        missing_mhcsf_df = (
            inspection["mhcsf_missing_per_column"]
            .rename_axis("Butir MHC-SF")
            .reset_index(name="Jumlah Missing")
        )

        st.dataframe(
            missing_mhcsf_df,
            use_container_width=True,
            hide_index=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Responden Lengkap",
                inspection["complete_rows"]
            )

        with col2:
            st.metric(
                "Responden Tidak Lengkap",
                inspection["incomplete_rows"]
            )

        st.subheader("Distribusi Kelengkapan Responden")

        st.dataframe(
            inspection["completeness_distribution"],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Detail Responden Tidak Lengkap")

        if not inspection["incomplete_details"].empty:
            st.dataframe(
                inspection["incomplete_details"],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("Semua responden memiliki jawaban MHC-SF lengkap.")

    else:
        st.warning("Struktur 14 butir MHC-SF belum terdeteksi.")

    # =====================================================
    # 11. DUPLICATE ANALYSIS
    # =====================================================

    st.divider()

    st.subheader("Duplicate Analysis")

    if inspection["duplicate_rows"] == 0:

        st.success(
            "Tidak ditemukan baris duplikat."
        )

    else:

        st.warning(
            f"Ditemukan {inspection['duplicate_rows']} "
            "baris duplikat."
        )

        with st.expander(
            "Lihat baris duplikat"
        ):

            duplicate_data = data[
                data.duplicated(keep=False)
            ]

            st.dataframe(
                duplicate_data,
                use_container_width=True,
                hide_index=True
            )

    # =====================================================
    # 12. COLUMN INFORMATION
    # =====================================================

    st.divider()

    st.subheader("Dataset Column Information")

    with st.expander(
        "Lihat seluruh nama kolom"
    ):

        for index, column in enumerate(
            data.columns,
            start=1
        ):

            st.write(
                f"{index}. {column}"
            )

    # =====================================================
    # 13. SAVE DATASET
    # =====================================================

    st.divider()

    st.subheader("Save Uploaded Dataset")

    st.info(
        "Dataset akan disimpan sebagai salinan mentah "
        "di folder data/uploaded/. Proses ini tidak "
        "mengubah dataset referensi maupun model aktif."
    )

    save_col1, save_col2 = st.columns(2)

    with save_col1:

        st.write(
            f"**Nama file:** {filename}"
        )

        st.write(
            f"**Ukuran:** {inspection['total_rows']:,} baris "
            f"x {inspection['total_columns']:,} kolom"
        )

    with save_col2:

        st.write(
            "**Lokasi penyimpanan:**"
        )

        st.code(
            "data/uploaded/"
        )

    if st.button(
        "Simpan Dataset",
        type="primary",
        use_container_width=True
    ):

        try:

            saved_path = save_uploaded_dataset(
                data,
                filename
            )

            st.success(
                "Dataset berhasil disimpan."
            )

            st.code(
                str(saved_path.relative_to(ROOT_DIR))
            )

        except Exception as error:

            st.error(
                f"Gagal menyimpan dataset: {error}"
            )

else:

    st.info(
        "Silakan upload dataset CSV atau Excel "
        "untuk memulai pemeriksaan."
    )
