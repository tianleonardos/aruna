import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction import predict_profile
from src.recommendations import generate_recommendations

# Menghasilkan prediksi dari model Aruna
prediction = predict_profile(
    emotional=3.5,
    social=2.0,
    psychological=3.0
)

# Menghasilkan rekomendasi berdasarkan hasil prediksi
recommendation = generate_recommendations(prediction)

print("=== HASIL REKOMENDASI ARUNA ===")
print("Profil:", recommendation["profile_name"])
print("Fokus:", recommendation["focus"])

print("\nRingkasan:")
print(recommendation["summary"])

print("\nRekomendasi:")
for i, item in enumerate(recommendation["recommendations"], start=1):
    print(f"{i}. {item}")

print("\nCatatan:")
print(recommendation["disclaimer"])
