import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.mhcsf_config import (
    MHC_SF_ITEMS,
    DIMENSIONS,
    RESPONSE_OPTIONS
)

print("Jumlah pertanyaan:", len(MHC_SF_ITEMS))

for dimension, config in DIMENSIONS.items():
    print(
        config["label"],
        ":", len(config["items"]), "pertanyaan"
    )

print("\nPilihan jawaban:")
for option in RESPONSE_OPTIONS:
    print(option["label"], "=", option["score"])
