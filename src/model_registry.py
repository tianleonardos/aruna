
from pathlib import Path
import json
import shutil
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ACTIVE_DIR = PROJECT_ROOT / "models" / "active"
VERSIONS_DIR = PROJECT_ROOT / "models" / "versions"

ACTIVE_MODEL = ACTIVE_DIR / "aruna_model_final.joblib"
REGISTRY_FILE = PROJECT_ROOT / "models" / "registry.json"


def initialize_registry():
    """Membuat registry awal berdasarkan model aktif."""

    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if not ACTIVE_MODEL.exists():
        raise FileNotFoundError(
            f"Model aktif tidak ditemukan: {ACTIVE_MODEL}"
        )

    if REGISTRY_FILE.exists():
        return load_registry()

    import joblib
    package = joblib.load(ACTIVE_MODEL)

    version = str(package.get("model_version", "1.0"))
    version_file = VERSIONS_DIR / f"aruna_model_v{version}.joblib"

    if not version_file.exists():
        shutil.copy2(ACTIVE_MODEL, version_file)

    registry = {
        "active_version": version,
        "models": [
            {
                "version": version,
                "filename": version_file.name,
                "status": "active",
                "registered_at": datetime.now().isoformat(
                    timespec="seconds"
                )
            }
        ]
    }

    save_registry(registry)
    return registry


def load_registry():
    """Membaca data registry."""

    if not REGISTRY_FILE.exists():
        raise FileNotFoundError(
            "Registry belum tersedia. Jalankan initialize_registry()."
        )

    with open(REGISTRY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_registry(registry):
    """Menyimpan perubahan registry."""

    with open(REGISTRY_FILE, "w", encoding="utf-8") as file:
        json.dump(registry, file, indent=4, ensure_ascii=False)


def get_model_history():
    """Menampilkan seluruh model yang tercatat."""

    registry = load_registry()
    return registry["models"]


def get_active_model_info():
    """Mengambil informasi model yang sedang aktif."""

    registry = load_registry()
    active_version = registry["active_version"]

    for model in registry["models"]:
        if model["version"] == active_version:
            return model

    raise ValueError("Informasi model aktif tidak ditemukan.")
