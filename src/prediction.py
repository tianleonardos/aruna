
from pathlib import Path

import joblib
import numpy as np

from src.preprocessing import (
    RESPONSE_MAPPING,
    DIMENSION_COLUMNS
)


# ============================================================
# 1. KONFIGURASI MODEL
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "active"
    / "aruna_model_final.joblib"
)

# Urutan 14 pertanyaan harus konsisten dengan preprocessing
ITEM_ORDER = (
    DIMENSION_COLUMNS["Emotional"]
    + DIMENSION_COLUMNS["Social"]
    + DIMENSION_COLUMNS["Psychological"]
)


# ============================================================
# 2. MEMUAT MODEL AKTIF
# ============================================================

def load_aruna_model():
    """Memuat paket model Aruna yang sedang aktif."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model Aruna tidak ditemukan: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


# ============================================================
# 3. PREDIKSI BERDASARKAN TIGA DIMENSI
# ============================================================

def predict_profile(emotional, social, psychological):
    """
    Memprediksi profil berdasarkan tiga skor dimensi.
    """

    package = load_aruna_model()

    features = np.array(
        [[emotional, social, psychological]],
        dtype=float
    )

    if not np.isfinite(features).all():
        raise ValueError("Skor harus berupa angka yang valid.")

    if features.min() < 0 or features.max() > 5:
        raise ValueError(
            "Skor dimensi harus berada pada rentang 0–5."
        )

    # Clustering kesejahteraan keseluruhan
    overall_label = package[
        "overall_model"
    ].predict(features)[0]

    # Clustering pola relatif antar dimensi
    personal_mean = features.mean(axis=1, keepdims=True)

    relative_features = features - personal_mean

    pattern_label = package[
        "pattern_model"
    ].predict(relative_features)[0]

    return {
        "overall_profile": package[
            "overall_label_map"
        ][overall_label],

        "pattern_profile": package[
            "pattern_label_map"
        ][pattern_label],

        "scores": {
            "Emotional": float(emotional),
            "Social": float(social),
            "Psychological": float(psychological)
        }
    }


# ============================================================
# 4. PREDIKSI LANGSUNG DARI 14 JAWABAN MHC-SF
# ============================================================

def predict_from_answers(answers):
    """
    Mengubah 14 jawaban MHC-SF menjadi profil Aruna.

    Input:
        answers:
            - List berisi 14 jawaban sesuai ITEM_ORDER
            - Atau dictionary dengan key Emotional_1,
              Social_1, dan seterusnya.

    Output:
        Skor setiap item, skor tiga dimensi,
        dan hasil clustering Aruna.
    """

    # --------------------------------------------------------
    # A. Validasi format input
    # --------------------------------------------------------

    if isinstance(answers, dict):

        missing_items = [
            item for item in ITEM_ORDER
            if item not in answers
        ]

        if missing_items:
            raise ValueError(
                f"Jawaban belum lengkap: {missing_items}"
            )

        raw_answers = [
            answers[item] for item in ITEM_ORDER
        ]

    elif isinstance(answers, (list, tuple)):

        if len(answers) != 14:
            raise ValueError(
                "Assessment harus berisi tepat 14 jawaban."
            )

        raw_answers = list(answers)

    else:
        raise TypeError(
            "Input harus berupa list, tuple, atau dictionary."
        )

    # --------------------------------------------------------
    # B. Konversi jawaban menjadi skor numerik
    # --------------------------------------------------------

    normalized_mapping = {
        key.casefold(): value
        for key, value in RESPONSE_MAPPING.items()
    }

    encoded_answers = []

    for index, answer in enumerate(raw_answers):

        if not isinstance(answer, str):
            raise ValueError(
                f"Jawaban nomor {index + 1} tidak valid."
            )

        normalized_answer = answer.strip().casefold()

        if normalized_answer not in normalized_mapping:
            raise ValueError(
                f"Jawaban nomor {index + 1} tidak dikenali: "
                f"{answer}"
            )

        encoded_answers.append(
            normalized_mapping[normalized_answer]
        )

    # --------------------------------------------------------
    # C. Menghubungkan skor dengan 14 item
    # --------------------------------------------------------

    item_scores = {
        item: float(score)
        for item, score in zip(
            ITEM_ORDER,
            encoded_answers
        )
    }

    # --------------------------------------------------------
    # D. Menghitung rata-rata tiga dimensi
    # --------------------------------------------------------

    dimension_scores = {}

    for dimension, columns in DIMENSION_COLUMNS.items():

        dimension_scores[dimension] = float(
            np.mean([
                item_scores[column]
                for column in columns
            ])
        )

    # --------------------------------------------------------
    # E. Prediksi menggunakan model Aruna
    # --------------------------------------------------------

    prediction = predict_profile(
        emotional=dimension_scores["Emotional"],
        social=dimension_scores["Social"],
        psychological=dimension_scores["Psychological"]
    )

    # --------------------------------------------------------
    # F. Menggabungkan hasil
    # --------------------------------------------------------

    return {
        "item_scores": item_scores,
        "dimension_scores": dimension_scores,
        "overall_profile": prediction["overall_profile"],
        "pattern_profile": prediction["pattern_profile"],
        "scores": prediction["scores"]
    }
