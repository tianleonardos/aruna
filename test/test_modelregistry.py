import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.model_registry import (
    initialize_registry,
    get_model_history,
    get_active_model_info
)

# Inisialisasi registry
registry = initialize_registry()

print("=== ARUNA MODEL REGISTRY ===")

print("\nVersi aktif:")
print(registry["active_version"])

print("\nInformasi model aktif:")
print(get_active_model_info())

print("\nRiwayat model:")
for model in get_model_history():
    print(model)
