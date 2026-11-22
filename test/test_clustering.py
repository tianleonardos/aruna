import os
import sys
import warnings
from pathlib import Path

# Redam warning Windows MKL KMeans agar output terminal bersih
os.environ["OMP_NUM_THREADS"] = "1"
warnings.filterwarnings("ignore")

# Pastikan root direktori ARUNA berada di sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
from src.preprocessing import preprocess_mhcsf_dataset
from src import clustering


def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title.upper()}")
    print("=" * 60)


def main():
    print_header("Pengujian Langsung Modul src/clustering.py (ARUNA)")
    print("Menjalankan setiap fungsi secara bertahap tanpa menggunakan framework eksternal.\n")

    # =========================================================================
    # 1. PERSIAPAN DATA RIIL DARI DATASET REFERENSI
    # =========================================================================
    print_header("1. Memuat & Menyiapkan Dataset Referensi")
    dataset_path = ROOT_DIR / "data" / "reference" / "thesis data set.xlsx"

    if not dataset_path.exists():
        print(f"[ERROR] File dataset referensi tidak ditemukan di: {dataset_path}")
        return

    raw_df = pd.read_excel(dataset_path)
    prep_result = preprocess_mhcsf_dataset(raw_df)

    data_14 = prep_result["features_14"]
    data_3 = prep_result["features_3"]

    print(f"Dataset berhasil dimuat dan dipreprocess:")
    print(f"- Representasi A_14 (14 butir): {data_14.shape}")
    print(f"- Representasi B_3 (3 dimensi): {data_3.shape}")

    # Uji prepare_experiment_data
    exp_data = clustering.prepare_experiment_data(data_14, data_3)
    print(f"[OK] prepare_experiment_data() sukses memvalidasi A_14 dan B_3.")

    # Uji prepare_features
    features_3 = clustering.prepare_features(data_3)
    print(f"[OK] prepare_features() sukses memverifikasi matriks 3 dimensi B_3.")


    # =========================================================================
    # 2. UJI TRANSFORMASI POLA RELATIF (RELATIVE PATTERN)
    # =========================================================================
    print_header("2. Uji Transformasi Deviasi Relatif (transform_relative_features)")
    relative_features = clustering.transform_relative_features(features_3)

    print("Contoh 3 responden pertama:")
    for i in range(3):
        skor_asli = features_3[i]
        skor_relatif = relative_features[i]
        mean_pribadi = skor_asli.mean()
        print(f"Responden {i+1}:")
        print(f"  - Asli [E, S, P]    : {np.round(skor_asli, 2)} (Rata-rata: {mean_pribadi:.2f})")
        print(f"  - Relatif [E',S',P']: {np.round(skor_relatif, 2)} (Jumlah deviasi: {skor_relatif.sum():.4f})")

    # Pastikan rata-rata deviasi tiap responden tepat 0
    max_deviation = np.max(np.abs(relative_features.mean(axis=1)))
    assert max_deviation < 1e-10, "Deviasi relatif harus berpusat di 0!"
    print(f"[OK] transform_relative_features() sukses (seluruh baris berpusat di 0, max deviasi = {max_deviation:.1e}).")


    # =========================================================================
    # 3. UJI ESTIMATOR KANDIDAT & METRIK EVALUASI INTERNAL
    # =========================================================================
    print_header("3. Uji Pelatihan Kandidat & Metrik Internal (_fit_candidate & _internal_metrics)")

    for algo in ["K-Means", "Agglomerative"]:
        model, labels = clustering._fit_candidate(algo, features_3, k=2)
        metrics = clustering._internal_metrics(features_3, labels)

        print(f"Algoritma: {algo} (k=2)")
        print(f"  - Silhouette Score       : {metrics['silhouette']:.4f} (lebih tinggi lebih baik)")
        print(f"  - Davies-Bouldin Index   : {metrics['davies_bouldin']:.4f} (lebih rendah lebih baik)")
        print(f"  - Calinski-Harabasz Index: {metrics['calinski_harabasz']:.2f} (lebih tinggi lebih baik)")

    # Uji kmedoids guard
    if clustering.kmedoids is None:
        print("\nCatatan: Library 'kmedoids' tidak terpasang di environment ini.")
        try:
            clustering._require_kmedoids()
        except ImportError as e:
            print(f"[OK] _require_kmedoids() menangani ketiadaan library dengan aman: {e}")
    else:
        km_model, km_labels = clustering._fit_candidate("K-Medoids", features_3, k=2)
        km_metrics = clustering._internal_metrics(features_3, km_labels)
        print(f"Algoritma: K-Medoids (k=2)")
        print(f"  - Silhouette Score       : {km_metrics['silhouette']:.4f}")
        print(f"  - Davies-Bouldin Index   : {km_metrics['davies_bouldin']:.4f}")
        print(f"  - Calinski-Harabasz Index: {km_metrics['calinski_harabasz']:.2f}")


    # =========================================================================
    # 4. UJI INTERPRETASI SEMANTIK CLUSTER
    # =========================================================================
    print_header("4. Uji Interpretasi Semantik Cluster")

    # Overall Interpretation
    km_overall, _ = clustering._fit_candidate("K-Means", features_3, k=2)
    overall_map = clustering.interpret_overall_clusters(km_overall)
    print("Hasil interpret_overall_clusters():")
    for cluster_id, label in overall_map.items():
        centroid = km_overall.cluster_centers_[cluster_id]
        print(f"  - Cluster {cluster_id} -> '{label}' (Centroid [E,S,P]: {np.round(centroid, 3)}, Rata-rata: {centroid.mean():.3f})")

    # Pattern Interpretation
    km_pattern, _ = clustering._fit_candidate("K-Means", relative_features, k=2)
    pattern_map = clustering.interpret_pattern_clusters(km_pattern)
    print("\nHasil interpret_pattern_clusters():")
    for cluster_id, label in pattern_map.items():
        centroid = km_pattern.cluster_centers_[cluster_id]
        print(f"  - Cluster {cluster_id} -> '{label}' (Centroid Relatif [E,S,P]: {np.round(centroid, 3)})")

    print("[OK] Interpretasi semantik cluster otomatis berjalan sesuai karakteristik centroid.")


    # =========================================================================
    # 5. UJI PERHITUNGAN THRESHOLD KUARTIL PERTAMA (Q1)
    # =========================================================================
    print_header("5. Uji Perhitungan Threshold Q1 (calculate_recommendation_thresholds)")
    q1_thresholds = clustering.calculate_recommendation_thresholds(features_3)
    print("Nilai Kuartil Pertama (Q1) dari 80% Data Training:")
    for dim, val in q1_thresholds.items():
        print(f"  - {dim:13s}: {val:.3f}")
    print("[OK] calculate_recommendation_thresholds() berhasil dihitung berdasarkan holdout split 80%.")


    # =========================================================================
    # 6. UJI PELATIHAN MODEL TWO-LAYER K-MEANS LENGKAP
    # =========================================================================
    print_header("6. Uji Pelatihan Model Two-Layer Final (train_two_layer_model)")
    two_layer_res = clustering.train_two_layer_model(data_3)
    package = two_layer_res["model_package"]

    print("Paket model yang dihasilkan:")
    print(f"  - Arsitektur         : {package['training_info']['architecture']}")
    print(f"  - Jumlah sampel latih: {package['training_info']['dataset_size']}")
    print(f"  - Overall Map        : {package['overall_label_map']}")
    print(f"  - Pattern Map        : {package['pattern_label_map']}")
    print(f"  - Threshold Q1       : {package['q1_thresholds']}")

    # Distribusi 4 profil pada dataset referensi
    overall_lbls = [package["overall_label_map"][l] for l in two_layer_res["overall_labels"]]
    pattern_lbls = [package["pattern_label_map"][l] for l in two_layer_res["pattern_labels"]]
    profil_kombinasi = [f"{o} - {p}" for o, p in zip(overall_lbls, pattern_lbls)]
    distribusi = pd.Series(profil_kombinasi).value_counts()

    print("\nDistribusi 4 Profil pada 332 Responden Referensi:")
    for profil, count in distribusi.items():
        pct = (count / len(profil_kombinasi)) * 100
        print(f"  - {profil:32s}: {count:3d} ({pct:.2f}%)")

    # Uji inferensi mandiri menggunakan model yang baru dilatih
    sample_student = np.array([[3.8, 1.8, 3.2]]) # Simulasi mahasiswa
    pred_overall_id = package["overall_model"].predict(sample_student)[0]
    sample_relative = sample_student - sample_student.mean(axis=1, keepdims=True)
    pred_pattern_id = package["pattern_model"].predict(sample_relative)[0]

    hasil_profil = f"{package['overall_label_map'][pred_overall_id]} - {package['pattern_label_map'][pred_pattern_id]}"
    print(f"\nUji Prediksi Mahasiswa Baru (Skor: E=3.8, S=1.8, P=3.2):")
    print(f"  -> Hasil Profil Terprediksi: {hasil_profil}")
    print("[OK] Model Two-Layer siap digunakan untuk inferensi operasional.")


    # =========================================================================
    # 7. UJI PEMILIHAN MODEL & PEMERINGKATAN (_rank_candidates)
    # =========================================================================
    print_header("7. Uji Logika Pemeringkatan Kandidat (_rank_candidates)")
    sample_candidates = pd.DataFrame({
        "algorithm": ["K-Means", "Agglomerative"],
        "silhouette": [0.4292, 0.3942],
        "davies_bouldin": [0.8497, 0.8532],
        "calinski_harabasz": [391.78, 305.87],
        "mean_ari": [0.9088, 0.4800],
    })
    ranked = clustering._rank_candidates(sample_candidates)
    print("Hasil pemeringkatan mean-rank:")
    print(ranked[["algorithm", "mean_rank", "selection_score", "selected"]].to_string(index=False))
    assert ranked.iloc[0]["algorithm"] == "K-Means"
    assert ranked.iloc[0]["selected"] is True or ranked.iloc[0]["selected"] == 1
    print("[OK] _rank_candidates() berhasil memilih kandidat terbaik berbasis mean-rank.")


    # =========================================================================
    # 8. UJI VALIDASI INPUT & KASUS SALAH (ERROR HANDLING)
    # =========================================================================
    print_header("8. Uji Penanganan Error & Validasi Input (Error Handling)")

    # Uji input 1 dimensi
    try:
        clustering._to_numpy(np.array([1, 2, 3]), name="Data_1D")
        print("[FAIL] Seharusnya menolak data 1D!")
    except ValueError as e:
        print(f"[OK] Berhasil menangkap input 1D: {e}")

    # Uji skor di luar rentang 0-5
    try:
        clustering._to_numpy(np.full((10, 3), 6.0), name="Data_Skor_6")
        print("[FAIL] Seharusnya menolak skor > 5!")
    except ValueError as e:
        print(f"[OK] Berhasil menangkap skor di luar rentang: {e}")

    # Uji jumlah responden kurang dari 6
    try:
        clustering._to_numpy(np.ones((4, 3)), name="Data_Sedikit")
        print("[FAIL] Seharusnya menolak data dengan baris < 6!")
    except ValueError as e:
        print(f"[OK] Berhasil menangkap data terlalu sedikit: {e}")

    # Uji urutan kolom DataFrame yang salah
    try:
        df_salah_kolom = pd.DataFrame(np.ones((10, 3)), columns=["Social", "Emotional", "Psychological"])
        clustering.prepare_features(df_salah_kolom)
        print("[FAIL] Seharusnya menolak urutan kolom yang tidak sesuai!")
    except ValueError as e:
        print(f"[OK] Berhasil menangkap urutan kolom yang keliru: {e}")


    print_header("SEMUA FUNGSI PADA src/clustering.py BERHASIL DIUJI DENGAN BAIK!")


if __name__ == "__main__":
    main()
