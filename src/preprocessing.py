
import re
import pandas as pd


# ============================================================
# 1. KONFIGURASI ARUNA
# ============================================================

STATUS_QUESTION = (
    "Are you a current undergraduate student "
    "at a Canadian university?"
)

QUESTION_PREFIX = (
    "During the past month, how often did you feel"
)

# Skor jawaban MHC-SF
RESPONSE_MAPPING = {
    "Never": 0,
    "Once or twice": 1,
    "About once a week": 2,
    "Once a week": 2,
    "About 2-3 times a week": 3,
    "Almost everyday": 4,
    "Everyday": 5
}

# Nama fitur berdasarkan dimensi MHC-SF
DIMENSION_COLUMNS = {
    "Emotional": [
        "Emotional_1",
        "Emotional_2",
        "Emotional_3"
    ],
    "Social": [
        "Social_1",
        "Social_2",
        "Social_3",
        "Social_4",
        "Social_5"
    ],
    "Psychological": [
        "Psychological_1",
        "Psychological_2",
        "Psychological_3",
        "Psychological_4",
        "Psychological_5",
        "Psychological_6"
    ]
}


# ============================================================
# 2. NORMALISASI NAMA KOLOM
# ============================================================

def normalize_column_name(name):
    """
    Menyamakan spasi biasa, non-breaking space,
    dan karakter whitespace lainnya.
    """
    return re.sub(r"\s+", " ", str(name)).strip().casefold()


# ============================================================
# 3. PREPROCESSING DATASET MHC-SF
# ============================================================

def preprocess_mhcsf_dataset(df):
    """
    Memvalidasi dan memproses dataset referensi Aruna.

    Tahapan:
    1. Validasi DataFrame.
    2. Identifikasi status mahasiswa aktif.
    3. Eksklusi responden non-mahasiswa aktif.
    4. Identifikasi 14 item MHC-SF.
    5. Normalisasi jawaban.
    6. Konversi jawaban menjadi skor 0-5.
    7. Identifikasi data lengkap.
    8. Menghasilkan laporan kualitas data.

    Returns
    -------
    complete_data : pandas.DataFrame
        Data numerik 14 item MHC-SF yang lengkap.

    report : dict
        Ringkasan hasil preprocessing.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input harus berupa pandas DataFrame."
        )

    data = df.copy()

    # --------------------------------------------------------
    # A. Identifikasi kolom status mahasiswa
    # --------------------------------------------------------

    status_matches = [
        col for col in data.columns
        if normalize_column_name(col)
        == normalize_column_name(STATUS_QUESTION)
    ]

    if len(status_matches) != 1:
        raise ValueError(
            "Kolom status mahasiswa aktif tidak ditemukan "
            "atau tidak teridentifikasi secara unik."
        )

    status_column = status_matches[0]

    # --------------------------------------------------------
    # B. Seleksi mahasiswa aktif
    # --------------------------------------------------------

    status_values = (
        data[status_column]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    active_mask = status_values.eq("yes").fillna(False)

    active_data = data.loc[active_mask].copy()

    excluded_rows = len(data) - len(active_data)

    # --------------------------------------------------------
    # C. Identifikasi 14 pertanyaan MHC-SF
    # --------------------------------------------------------

    mhcsf_columns = [
        col for col in active_data.columns
        if normalize_column_name(col).startswith(
            normalize_column_name(QUESTION_PREFIX)
        )
    ]

    if len(mhcsf_columns) != 14:
        raise ValueError(
            f"Ditemukan {len(mhcsf_columns)} item MHC-SF. "
            "Dataset harus memiliki tepat 14 item."
        )

    mhcsf_data = active_data[mhcsf_columns].copy()

    # --------------------------------------------------------
    # D. Normalisasi jawaban
    # --------------------------------------------------------

    for col in mhcsf_columns:
        mhcsf_data[col] = (
            mhcsf_data[col]
            .astype("string")
            .str.strip()
        )

    # Jawaban yang memang tidak memberikan skor
    # diperlakukan sebagai missing value.
    mhcsf_data = mhcsf_data.replace({
        "Prefer not to answer": pd.NA,
        "": pd.NA
    })

    # --------------------------------------------------------
    # E. Validasi kategori jawaban
    # --------------------------------------------------------

    observed_values = set(
        mhcsf_data.stack().dropna().unique()
    )

    unknown_values = observed_values - set(RESPONSE_MAPPING)

    if unknown_values:
        raise ValueError(
            "Ditemukan kategori jawaban yang belum "
            f"terdaftar: {sorted(unknown_values)}"
        )

    # --------------------------------------------------------
    # F. Konversi jawaban menjadi skor numerik
    # --------------------------------------------------------

    encoded_data = mhcsf_data.replace(RESPONSE_MAPPING)

    encoded_data = encoded_data.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # G. Penamaan 14 fitur
    # --------------------------------------------------------

    new_columns = (
        DIMENSION_COLUMNS["Emotional"]
        + DIMENSION_COLUMNS["Social"]
        + DIMENSION_COLUMNS["Psychological"]
    )

    encoded_data.columns = new_columns

    # --------------------------------------------------------
    # H. Identifikasi data lengkap
    # --------------------------------------------------------

    complete_mask = encoded_data.notna().all(axis=1)

    complete_data = encoded_data.loc[
        complete_mask
    ].copy()

    incomplete_rows = int((~complete_mask).sum())

    # --------------------------------------------------------
    # I. Laporan kualitas data
    # --------------------------------------------------------

    report = {
        "total_rows": len(data),
        "active_students": len(active_data),
        "excluded_non_active": excluded_rows,
        "total_mhcsf_items": len(mhcsf_columns),
        "complete_rows": len(complete_data),
        "incomplete_rows": incomplete_rows,
        "missing_values": int(
            encoded_data.isna().sum().sum()
        ),
        "score_min": (
            float(complete_data.min().min())
            if not complete_data.empty else None
        ),
        "score_max": (
            float(complete_data.max().max())
            if not complete_data.empty else None
        )
    }

    return complete_data, report


# ============================================================
# 4. PEMBENTUKAN SKOR TIGA DIMENSI
# ============================================================

def calculate_dimension_scores(processed_data):
    """
    Menghitung rata-rata skor Emotional, Social,
    dan Psychological untuk setiap responden.
    """

    if not isinstance(processed_data, pd.DataFrame):
        raise TypeError(
            "Input harus berupa pandas DataFrame."
        )

    required_columns = [
        col
        for columns in DIMENSION_COLUMNS.values()
        for col in columns
    ]

    missing_columns = [
        col for col in required_columns
        if col not in processed_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Kolom fitur tidak lengkap: {missing_columns}"
        )

    if processed_data[required_columns].isna().any().any():
        raise ValueError(
            "Data mengandung missing value. "
            "Gunakan data hasil preprocessing lengkap."
        )

    scores = pd.DataFrame(index=processed_data.index)

    for dimension, columns in DIMENSION_COLUMNS.items():
        scores[dimension] = processed_data[columns].mean(
            axis=1
        )

    return scores    