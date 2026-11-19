import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction import load_aruna_model, predict_profile

# Tes pemuatan model
model = load_aruna_model()

print("Model berhasil dimuat!")
print("Versi:", model["model_version"])

# Tes prediksi dengan contoh skor
result = predict_profile(
    emotional=3.5,
    social=2.0,
    psychological=3.0
)

print("\nHasil prediksi:")
print(result)
