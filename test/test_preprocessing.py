import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import pandas as pd

from src.preprocessing import (
    preprocess_mhcsf_dataset,
    calculate_dimension_scores
)

# Lokasi dataset referensi
DATA_PATH = "data/reference/thesis data set.xlsx"

# Membaca dataset
df = pd.read_excel(DATA_PATH)

# Menjalankan preprocessing
processed_data, report = preprocess_mhcsf_dataset(df)

# Membentuk tiga skor dimensi
dimension_scores = calculate_dimension_scores(
    processed_data
)

print("=== ARUNA DATA PREPROCESSING ===")

print("\nLaporan kualitas data:")
for key, value in report.items():
    print(f"{key}: {value}")

print("\nLima baris pertama - 14 item MHC-SF:")
print(processed_data.head())

print("\nLima baris pertama - 3 dimensi:")
print(dimension_scores.head())

print("\nInformasi dataset:")
print(processed_data.info())
