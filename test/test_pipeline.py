import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.pipeline import assess_student


# Simulasi jawaban mahasiswa
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


# Menjalankan seluruh pipeline
result = assess_student(sample_answers)


print("=" * 50)
print("HASIL ASSESSMENT ARUNA")
print("=" * 50)

print("\n1. SKOR DIMENSI")

for dimension, score in result["dimension_scores"].items():
    print(f"{dimension}: {score:.2f}")


print("\n2. PROFIL KESEJAHTERAAN")

print("Overall:", result["overall_profile"])
print("Pattern:", result["pattern_profile"])


print("\n3. RINGKASAN PROFIL")

recommendation = result["recommendation"]

print("Nama Profil:", recommendation["profile_name"])
print("Ringkasan:", recommendation["summary"])
print("Fokus:", recommendation["focus"])


print("\n4. REKOMENDASI")

for index, item in enumerate(
    recommendation["recommendations"], start=1
):
    print(f"{index}. {item}")


print("\n5. DISCLAIMER")

print(recommendation["disclaimer"])


print("\n" + "=" * 50)
print("ARUNA PIPELINE BERHASIL DIJALANKAN")
print("=" * 50)

from src.pipeline import assess_student

result = assess_student(sample_answers)

print("\n=== FULL ARUNA PIPELINE ===")
print("Dimension scores:", result["dimension_scores"])
print("Overall profile:", result["overall_profile"])
print("Pattern profile:", result["pattern_profile"])
print("Recommendation:", result["recommendation"])