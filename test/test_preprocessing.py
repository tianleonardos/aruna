import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import pandas as pd
from src.preprocessing import preprocess_mhcsf_dataset

# Baca dataset
df = pd.read_excel("data/reference/thesis data set.xlsx")

# Jalankan preprocessing
result = preprocess_mhcsf_dataset(df)

# Tampilkan summary
print(result["summary"])
print("Encoded:", result["encoded_df"].shape)
print("Complete:", result["complete_df"].shape)
print("Features 14:", result["features_14"].shape)
print("Features 3:", result["features_3"].shape)

print("\nMissing value pada features_14:")
print(result["features_14"].isna().sum().sum())

print("\nKolom fitur 3:")
print(result["features_3"].columns.tolist())

from src.preprocessing import get_invalid_response_values

# Salin data untuk pengujian
test_df = result["analysis_df"].copy()

# 1. Respons valid dengan spasi tambahan
test_df.iloc[0, test_df.columns.get_loc("MHC_01")] = " Never "

print("Uji spasi:", get_invalid_response_values(test_df))

# 2. Respons dengan kapitalisasi berbeda
test_df = result["analysis_df"].copy()
test_df.iloc[0, test_df.columns.get_loc("MHC_01")] = "never"

print("Uji kapitalisasi:", get_invalid_response_values(test_df))

# 3. Respons yang benar-benar tidak dikenal
test_df = result["analysis_df"].copy()
test_df.iloc[0, test_df.columns.get_loc("MHC_01")] = "Very Often"

print("Uji kategori asing:", get_invalid_response_values(test_df))

from src.preprocessing import calculate_dimension_scores

import pandas as pd
from src.preprocessing import calculate_dimension_scores

sample_answers = pd.Series({
    "MHC_01": 0,
    "MHC_02": 1,
    "MHC_03": 2,
    "MHC_04": 3,
    "MHC_05": 4,
    "MHC_06": 5,
    "MHC_07": 0,
    "MHC_08": 1,
    "MHC_09": 2,
    "MHC_10": 3,
    "MHC_11": 4,
    "MHC_12": 5,
    "MHC_13": 0,
    "MHC_14": 1,
})

scores = calculate_dimension_scores(sample_answers)

print("Hasil perhitungan:")
print(scores)

from src.preprocessing import calculate_dimension_scores

test_cases = {
    "Jumlah kurang": {"MHC_01": 2},
    "Skor di luar rentang": {
        **{f"MHC_{i:02d}": 2 for i in range(1, 15)},
        "MHC_14": 6,
    },
}

for name, answers in test_cases.items():
    try:
        calculate_dimension_scores(answers)
        print(f"{name}: TIDAK TERDETEKSI")
    except (ValueError, TypeError, KeyError) as e:
        print(f"{name}: Berhasil ditolak ({type(e).__name__})")

from src.preprocessing import preprocess_student_answers

sample_answers = [
    "Never",
    "Once or twice",
    "About once a week",
    "About 2-3 times a week",
    "Almost everyday",
    "Everyday",
    "Never",
    "Once or twice",
    "About once a week",
    "About 2-3 times a week",
    "Almost everyday",
    "Everyday",
    "Never",
    "Once or twice",
]

result = preprocess_student_answers(sample_answers)

print("\n=== HASIL PREPROCESSING JAWABAN MAHASISWA ===")
print("Item scores:", result["item_scores"])
print("Dimension scores:", result["dimension_scores"])
print("Model features:", result["model_features"])        

from src.prediction import predict_from_answers

prediction = predict_from_answers(sample_answers)

print("\n=== HASIL PREDIKSI ARUNA ===")
print("Dimension scores:", prediction["dimension_scores"])
print("Overall profile:", prediction["overall_profile"])
print("Pattern profile:", prediction["pattern_profile"])
print("Scores:", prediction["scores"])

from src.mhcsf_config import MHC_SF_ITEMS
from src.preprocessing import (
    ITEM_COLUMNS,
    DIMENSION_COLUMNS,
    FEATURE_COLUMNS,
)

print("\n=== AUDIT KONFIGURASI MHC-SF ===")

# 1. Audit jumlah dan urutan pertanyaan
question_ids = [
    f"MHC_{item['id']:02d}"
    for item in MHC_SF_ITEMS
]

print("Jumlah pertanyaan:", len(MHC_SF_ITEMS))
print("Urutan ID benar:", question_ids == ITEM_COLUMNS)
print("ID konfigurasi:", question_ids)
print("ID preprocessing:", ITEM_COLUMNS)

# 2. Audit pembagian dimensi
for dimension, items in DIMENSION_COLUMNS.items():
    print(f"{dimension}: {len(items)} butir")

# 3. Audit urutan fitur model
print("\nUrutan fitur preprocessing:", FEATURE_COLUMNS)

expected_features = [
    "Emotional",
    "Social",
    "Psychological",
]

print(
    "Urutan fitur sesuai:",
    FEATURE_COLUMNS == expected_features
)

# 4. Audit dimensi pada konfigurasi pertanyaan
print("\nDistribusi dimensi pertanyaan:")

for dimension in expected_features:
    count = sum(
        item["dimension"] == dimension
        for item in MHC_SF_ITEMS
    )
    print(f"{dimension}: {count} pertanyaan")

    print("\nID dari konfigurasi:", question_ids)
print("ID dari preprocessing:", ITEM_COLUMNS)

print("\n=== AUDIT PEMETAAN DIMENSI ===")

for dimension, columns in DIMENSION_COLUMNS.items():

    configured_items = [
        f"MHC_{item['id']:02d}"
        for item in MHC_SF_ITEMS
        if item["dimension"] == dimension
    ]

    print(f"\n{dimension}")
    print("Konfigurasi:", configured_items)
    print("Preprocessing:", columns)
    print("Sesuai:", configured_items == columns)