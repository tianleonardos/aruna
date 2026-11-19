
import sys
import subprocess
import importlib
import importlib.metadata

REQUIRED_LIBRARIES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "scikit-learn": "sklearn",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "streamlit": "streamlit",
    "joblib": "joblib",
    "scipy": "scipy",
    "plotly": "plotly",
}

def check_and_install():

    print("=" * 55)
    print("       ARUNA ENVIRONMENT SETUP")
    print("=" * 55)

    missing = []

    for package, module in REQUIRED_LIBRARIES.items():
        try:
            importlib.import_module(module)
            version = importlib.metadata.version(package)
            print(f"[OK] {package} ({version})")

        except (ImportError, importlib.metadata.PackageNotFoundError):
            print(f"[MISSING] {package}")
            missing.append(package)

    if missing:
        print("\nInstalling missing libraries...\n")

        subprocess.check_call([
            sys.executable, "-m", "pip",
            "install", *missing
        ])

        print("\nInstallation completed!")

    else:
        print("\nAll libraries are already installed!")

    print("\nValidating installation...")

    for package, module in REQUIRED_LIBRARIES.items():
        try:
            importlib.import_module(module)
            print(f"[OK] {package}")

        except ImportError:
            print(f"[FAILED] {package}")

    print("\nARUNA ENVIRONMENT READY!")


if __name__ == "__main__":
    check_and_install()
