import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction import predict_from_answers


# Simulasi 14 jawaban mahasiswa
sample_answers = [
    "Almost everyday",
    "About once a week",
    "Once or twice",

    "Never",
    "About 2-3 times a week",
    "Never",
    "About once a week",
    "Never",

    "Everyday",
    "About once a week",
    "Once or twice",
    "About 2-3 times a week",
    "Once or twice",
    "Once or twice"
]


# Menjalankan pipeline prediksi
result = predict_from_answers(sample_answers)


print("=== ARUNA PREDICTION PIPELINE ===")

print("\nSkor 14 item:")
for item, score in result["item_scores"].items():
    print(f"{item}: {score}")

print("\nSkor tiga dimensi:")
for dimension, score in result["dimension_scores"].items():
    print(f"{dimension}: {score:.2f}")

print("\nHasil clustering:")
print("Overall Profile:", result["overall_profile"])
print("Pattern Profile:", result["pattern_profile"])

print("\nPipeline berhasil dijalankan!")

