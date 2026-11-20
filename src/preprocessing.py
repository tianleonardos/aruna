
import re
import unicodedata

import numpy as np
import pandas as pd


# =========================================================
# 1. KONFIGURASI PREPROCESSING ARUNA
# Mengikuti notebook final.
# =========================================================

ITEM_COLUMNS = [f"MHC_{i:02d}" for i in range(1, 15)]

DIMENSION_COLUMNS = {
    "Emotional": ["MHC_01", "MHC_02", "MHC_03"],
    "Social": ["MHC_04", "MHC_05", "MHC_06", "MHC_07", "MHC_08"],
    "Psychological": [
        "MHC_09", "MHC_10", "MHC_11",
        "MHC_12", "MHC_13", "MHC_14"
    ]
}

DIMENSION_ITEMS = DIMENSION_COLUMNS
FEATURE_COLUMNS = ["Emotional", "Social", "Psychological"]

STATUS_COLUMN = "Current_Undergraduate"
STATUS_VALUE = "Yes"

STATUS_COLUMN_ALIASES = [
    "Current_Undergraduate",
    "Are you a current undergraduate student at a Canadian university?"
]

QUESTION_PREFIX = "During the past month, how often did you feel"

RESPONSE_MAPPING = {
    "Never": 0,
    "Once or twice": 1,
    "About once a week": 2,
    "About 2-3 times a week": 3,
    "Almost everyday": 4,
    "Everyday": 5
}

# Sesuai notebook:
# Alias hanya diterapkan pada MHC_03.
RESPONSE_ALIASES = {
    "MHC_03": {
        "Once a week": "About once a week"
    }
}

MISSING_RESPONSES = [
    "Prefer not to answer",
    "",
    " "
]


# =========================================================
# 2. UTILITAS NORMALISASI
# =========================================================

def normalize_column_name(column):
    """
    Membersihkan nama kolom:
    - Unicode normalization.
    - Non-breaking space.
    - Zero-width characters.
    - Spasi berulang.
    - Spasi di awal dan akhir.
    """
    column = unicodedata.normalize("NFKC", str(column))

    column = (
        column
        .replace("\xa0", " ")
        .replace("\u200b", "")
        .replace("\ufeff", "")
    )

    column = re.sub(r"\s+", " ", column)

    return column.strip()


def normalize_response(value, item=None):
    if pd.isna(value):
        return pd.NA

    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\u00A0", " ")
    text = text.strip()

    if text in MISSING_RESPONSES:
        return pd.NA

    aliases = RESPONSE_ALIASES.get(item, {})
    text = aliases.get(text, text)

    response_lookup = {
        key.casefold(): key
        for key in RESPONSE_MAPPING
    }

    return response_lookup.get(text.casefold(), text)

def normalize_dataframe_columns(df):
    """
    Menghasilkan salinan DataFrame dengan nama kolom
    yang sudah dinormalisasi.

    Menolak nama kolom yang menjadi duplikat setelah normalisasi.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input harus berupa pandas DataFrame.")

    result = df.copy()

    normalized_columns = [
        normalize_column_name(column)
        for column in result.columns
    ]

    if len(normalized_columns) != len(set(normalized_columns)):
        raise ValueError(
            "Terdapat nama kolom duplikat setelah normalisasi. "
            "Periksa spasi atau karakter tersembunyi pada header."
        )

    result.columns = normalized_columns

    return result


# =========================================================
# 3. DETEKSI KOLOM DATASET
# =========================================================

def detect_mhcsf_columns(df):
    """
    Mendeteksi 14 kolom MHC-SF.

    Mendukung:
    1. Nama standar MHC_01 sampai MHC_14.
    2. Nama pertanyaan asli dari dataset.

    PENTING:
    Fungsi mengembalikan nama kolom AKTUAL pada DataFrame,
    bukan nama hasil normalisasi yang belum tentu tersedia
    sebagai label kolom DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input harus berupa pandas DataFrame.")

    actual_columns = list(df.columns)

    normalized_to_actual = {}

    for column in actual_columns:
        normalized = normalize_column_name(column)

        key = normalized.casefold()

        if key in normalized_to_actual:
            raise ValueError(
                f"Kolom duplikat setelah normalisasi: {normalized!r}"
            )

        normalized_to_actual[key] = column

    # Prioritas 1: nama kolom standar.
    standard_keys = [
        item.casefold() for item in ITEM_COLUMNS
    ]

    if all(key in normalized_to_actual for key in standard_keys):
        return [
            normalized_to_actual[key]
            for key in standard_keys
        ]

    # Prioritas 2: nama pertanyaan asli.
    prefix = normalize_column_name(QUESTION_PREFIX).casefold()

    detected = [
        column
        for column in actual_columns
        if normalize_column_name(column).casefold().startswith(prefix)
    ]

    if len(detected) == 14:
        return detected

    raise ValueError(
        "Kolom MHC-SF tidak terdeteksi dengan benar. "
        f"Ditemukan {len(detected)} dari 14 kolom yang dibutuhkan."
    )


def detect_status_column(df):
    """Mendeteksi kolom status mahasiswa aktif."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input harus berupa pandas DataFrame.")

    normalized_to_actual = {
        normalize_column_name(column).casefold(): column
        for column in df.columns
    }

    for alias in STATUS_COLUMN_ALIASES:
        key = normalize_column_name(alias).casefold()

        if key in normalized_to_actual:
            return normalized_to_actual[key]

    raise ValueError(
        "Kolom status mahasiswa tidak ditemukan. "
        "Kolom yang diharapkan adalah Current_Undergraduate "
        "atau pertanyaan status mahasiswa asli."
    )


# =========================================================
# 4. VALIDASI STRUKTUR DATASET
# =========================================================

def validate_mhcsf_structure(df):
    """
    Memeriksa keberadaan 14 item MHC-SF dan kolom status.
    """
    result = {
        "valid": False,
        "mhcsf_columns": [],
        "status_column": None,
        "errors": []
    }

    try:
        result["mhcsf_columns"] = detect_mhcsf_columns(df)
    except (ValueError, TypeError) as error:
        result["errors"].append(str(error))

    try:
        result["status_column"] = detect_status_column(df)
    except (ValueError, TypeError) as error:
        result["errors"].append(str(error))

    result["valid"] = len(result["errors"]) == 0

    return result


def get_invalid_response_values(df, mhcsf_columns=None):
    """
    Mengidentifikasi kategori jawaban yang tidak dikenali.
    """
    if mhcsf_columns is None:
        mhcsf_columns = detect_mhcsf_columns(df)

    invalid_values = {}

    for item, column in zip(ITEM_COLUMNS, mhcsf_columns):
        if column not in df.columns:
            raise KeyError(
                f"Kolom {column!r} tidak tersedia pada DataFrame."
            )

        invalid = []

        for value in df[column].dropna().unique():
            normalized = normalize_response(value, item=item)

            if pd.isna(normalized):
                continue

            if normalized not in RESPONSE_MAPPING:
                invalid.append(value)

        if invalid:
            invalid_values[column] = invalid

    return invalid_values


# =========================================================
# 5. RENAME KOLOM MHC-SF
# =========================================================

def rename_mhcsf_columns(df):
    """
    Mengubah nama 14 item menjadi MHC_01 sampai MHC_14.

    Nama kolom lainnya tetap dipertahankan.
    """
    result = normalize_dataframe_columns(df)

    detected_columns = detect_mhcsf_columns(result)

    rename_mapping = {
        old_name: new_name
        for old_name, new_name in zip(
            detected_columns,
            ITEM_COLUMNS
        )
    }

    result = result.rename(columns=rename_mapping)

    # Normalisasi nama kolom status.
    status_column = detect_status_column(result)

    if status_column != STATUS_COLUMN:
        if STATUS_COLUMN in result.columns:
            raise ValueError(
                f"Kolom {STATUS_COLUMN} sudah tersedia."
            )

        result = result.rename(
            columns={status_column: STATUS_COLUMN}
        )

    return result


# =========================================================
# 6. ENCODING JAWABAN
# =========================================================

def encode_response(value, item=None):
    """
    Mengubah satu kategori jawaban menjadi skor ordinal 0–5.
    """
    normalized = normalize_response(value, item=item)

    if pd.isna(normalized):
        return pd.NA

    if normalized not in RESPONSE_MAPPING:
        raise ValueError(
            f"Kategori jawaban tidak dikenali untuk "
            f"{item or 'item MHC-SF'}: {value!r}"
        )

    return RESPONSE_MAPPING[normalized]


# =========================================================
# 7. PREPROCESSING DATASET REFERENSI
# =========================================================

def preprocess_mhcsf_dataset(df):
    """
    Preprocessing dataset referensi Aruna.

    Urutan:
    1. Normalisasi nama kolom.
    2. Rename 14 item MHC-SF.
    3. Seleksi mahasiswa aktif.
    4. Normalisasi respons.
    5. Encoding ordinal.
    6. Complete-case selection.
    7. Pembentukan fitur 14 item dan 3 dimensi.

    Seluruh aturan mengikuti notebook final.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Dataset harus berupa pandas DataFrame.")

    if df.empty:
        raise ValueError("Dataset tidak boleh kosong.")

    # 1. Normalisasi nama kolom.
    source_df = normalize_dataframe_columns(df)

    # 2. Rename item dan status.
    renamed_df = rename_mhcsf_columns(source_df)

    # 3. Seleksi mahasiswa aktif.

    status_values = renamed_df[STATUS_COLUMN].map(
        lambda value: (
            normalize_column_name(value).casefold()
            if pd.notna(value)
            else None
        )
    )

    analysis_df = renamed_df[
        status_values == STATUS_VALUE.casefold()
    ].copy()


    if analysis_df.empty:
        raise ValueError(
            "Tidak ditemukan responden dengan status "
            "mahasiswa aktif (Yes)."
        )

    # 4. Pastikan seluruh item tersedia.
    missing_columns = [
        column for column in ITEM_COLUMNS
        if column not in analysis_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Kolom MHC-SF tidak lengkap: {missing_columns}"
        )

    # 5. Normalisasi respons per item.
    for item in ITEM_COLUMNS:
        analysis_df[item] = analysis_df[item].map(
            lambda value: normalize_response(
                value,
                item=item
            )
        )

    # 6. Encoding ordinal.
    encoded_df = analysis_df.copy()

    for item in ITEM_COLUMNS:
        encoded_df[item] = encoded_df[item].map(
            lambda value: encode_response(
                value,
                item=item
            )
        ).astype("Int64")

    # 7. Seleksi complete-case.
    complete_df = encoded_df.dropna(
        subset=ITEM_COLUMNS
    ).copy()

    if complete_df.empty:
        raise ValueError(
            "Tidak ada responden dengan jawaban lengkap "
            "pada 14 item MHC-SF."
        )

    # 8. Representasi 14 fitur.
    features_14 = complete_df[ITEM_COLUMNS].copy()

    # 9. Representasi 3 dimensi.
    features_3 = pd.DataFrame(index=complete_df.index)

    for dimension, items in DIMENSION_COLUMNS.items():
        features_3[dimension] = complete_df[items].mean(axis=1)

    # 10. Ringkasan preprocessing.
    missing_per_item = analysis_df[ITEM_COLUMNS].isna().sum()

    missing_per_respondent = (
        encoded_df[ITEM_COLUMNS].isna().sum(axis=1)
    )

    summary = {
        "total_rows": int(len(source_df)),
        "active_students": int(len(analysis_df)),
        "excluded_non_active": int(
            len(source_df) - len(analysis_df)
        ),
        "total_mhcsf_items": len(ITEM_COLUMNS),
        "complete_rows": int(len(complete_df)),
        "incomplete_rows": int(
            (missing_per_respondent > 0).sum()
        ),
        "missing_values": int(missing_per_item.sum()),
        "score_min": 0,
        "score_max": 5
    }

    return {
        "source_df": source_df,
        "analysis_df": analysis_df,
        "encoded_df": encoded_df,
        "complete_df": complete_df,
        "features_14": features_14,
        "features_3": features_3,
        "summary": summary
    }


# =========================================================
# 8. PEMBENTUKAN SKOR DIMENSI
# =========================================================

def calculate_dimension_scores(item_scores):
    """
    Menghitung rata-rata Emotional, Social, dan Psychological.
    """
    if isinstance(item_scores, pd.Series):
        item_scores = item_scores.to_dict()

    if not isinstance(item_scores, dict):
        raise TypeError(
            "item_scores harus berupa dictionary "
            "atau pandas Series."
        )

    missing_items = [
        item for item in ITEM_COLUMNS
        if item not in item_scores
    ]

    if missing_items:
        raise ValueError(
            f"Skor item belum lengkap: {missing_items}"
        )

    dimension_scores = {}

    for dimension, items in DIMENSION_COLUMNS.items():
        values = []

        for item in items:
            value = item_scores[item]

            if pd.isna(value):
                raise ValueError(
                    f"Skor {item} belum tersedia."
                )

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                raise ValueError(
                    f"Skor {item} harus berupa angka."
                )

            if not np.isfinite(numeric_value):
                raise ValueError(
                    f"Skor {item} tidak valid."
                )

            if not 0 <= numeric_value <= 5:
                raise ValueError(
                    f"Skor {item} harus berada pada rentang 0–5."
                )

            values.append(numeric_value)

        dimension_scores[dimension] = float(np.mean(values))

    return dimension_scores


# =========================================================
# 9. PREPROCESSING JAWABAN MAHASISWA
# =========================================================

def preprocess_student_answers(answers):
    """
    Memproses 14 jawaban mahasiswa untuk inferensi model.

    Input:
    - List/tuple 14 jawaban sesuai urutan MHC-SF.
    - Dictionary dengan key MHC_01 sampai MHC_14.

    Output:
    - item_scores
    - dimension_scores
    - model_features
    """
    if isinstance(answers, (list, tuple)):
        if len(answers) != 14:
            raise ValueError(
                "Asesmen harus berisi tepat 14 jawaban."
            )

        answer_dict = dict(
            zip(ITEM_COLUMNS, answers)
        )

    elif isinstance(answers, dict):
        answer_dict = answers.copy()

    else:
        raise TypeError(
            "Jawaban harus berupa list, tuple, atau dictionary."
        )

    item_scores = {}

    for item in ITEM_COLUMNS:
        if item not in answer_dict:
            raise ValueError(
                f"Jawaban {item} belum tersedia."
            )

        score = encode_response(
            answer_dict[item],
            item=item
        )

        if pd.isna(score):
            raise ValueError(
                f"Jawaban {item} belum diisi."
            )

        item_scores[item] = int(score)

    dimension_scores = calculate_dimension_scores(
        item_scores
    )

    model_features = [
        dimension_scores[column]
        for column in FEATURE_COLUMNS
    ]

    return {
        "item_scores": item_scores,
        "dimension_scores": dimension_scores,
        "model_features": model_features
    }
