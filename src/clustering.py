"""Eksperimen clustering dan pelatihan model Two-Layer Aruna.

Rancangan eksperimen utama mengikuti 02_Aruna_Notebook_Final.ipynb:
- Algoritma kandidat: K-Means, K-Medoids, dan Agglomerative.
- Representasi fitur: A_14 (14 butir MHC-SF) dan B_3 (3 skor dimensi).
- Kandidat jumlah cluster: k = 2 sampai 6.
- Metrik internal: Silhouette, Davies-Bouldin, dan Calinski-Harabasz.
- Stabilitas: 30 subsampling, masing-masing menggunakan 80% data,
  pada B_3 dengan k=2 dan dibandingkan menggunakan pairwise ARI.
- Model final Two-Layer pada notebook: K-Means k=2 untuk Overall dan
  fitur B_3 yang dipusatkan per responden untuk Relative Pattern.

Pemilihan algoritma otomatis adalah tambahan pada tingkat aplikasi.
Notebook membandingkan metrik, tetapi tidak menetapkan satu skor gabungan.
Modul ini menggunakan aturan mean-rank dengan bobot yang sama dan tetap
mengembalikan seluruh skor komponen agar keputusan dapat diaudit.

Interpretasi Pattern Cluster:
- Centroid Pattern berada pada ruang fitur relatif (setiap baris responden
  dikurangi rata-rata tiga dimensinya).
- Dimensi dengan nilai centroid paling rendah dapat ditafsirkan sebagai
  dimensi yang relatif lebih rendah.
- Interpretasi hanya diberikan jika jarak dimensi terendah ke dimensi
  terendah kedua mencapai PATTERN_MIN_GAP.
- Ambang interpretasi adalah aturan aplikasi, bukan parameter yang berasal
  dari notebook atau batas klinis. Nilainya perlu diuji sensitivitasnya.
"""

from __future__ import annotations

from datetime import datetime
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split

try:
    import kmedoids
except ImportError as exc:  # pragma: no cover - bergantung pada environment
    kmedoids = None
    _KMEDOIDS_IMPORT_ERROR = exc
else:
    _KMEDOIDS_IMPORT_ERROR = None


# ---------------------------------------------------------------------------
# Konfigurasi eksperimen
# ---------------------------------------------------------------------------

FEATURE_COLUMNS = ["Emotional", "Social", "Psychological"]
ITEM_FEATURE_COUNT = 14

RANDOM_STATE = 42
K_RANGE = range(2, 7)
N_INIT = 20

N_STABILITY_RUNS = 30
STABILITY_SAMPLE_FRACTION = 0.8

ALGORITHM_ORDER = ("K-Means", "K-Medoids", "Agglomerative")
REPRESENTATIONS = ("A_14", "B_3")

# Ambang minimum selisih centroid relatif agar suatu dimensi diberi label
# "Relatif Rendah". Satuan mengikuti skor rata-rata MHC-SF (0-5).
#
# Ini merupakan aturan interpretasi aplikasi, bukan hasil eksperimen notebook
# atau batas psikometrik/klinis. Lakukan analisis sensitivitas sebelum
# menetapkan nilai ini sebagai aturan final.
PATTERN_MIN_GAP = 0.25

# Nama dimensi untuk tampilan profil. Urutannya harus sama dengan
# FEATURE_COLUMNS karena indeks centroid mengikuti urutan fitur tersebut.
PATTERN_DIMENSION_LABELS = {
    "Emotional": "Emosional Relatif Rendah",
    "Social": "Sosial Relatif Rendah",
    "Psychological": "Psikologis Relatif Rendah",
}


# ---------------------------------------------------------------------------
# Validasi input dan representasi fitur
# ---------------------------------------------------------------------------

def _to_numpy(
    data: Any,
    *,
    name: str,
    expected_columns: int | None = None,
) -> np.ndarray:
    """Mengubah input menjadi matriks numerik dan memvalidasi skornya.

    Parameters
    ----------
    data:
        DataFrame pandas atau array dua dimensi.
    name:
        Nama representasi data untuk pesan kesalahan.
    expected_columns:
        Jumlah kolom yang diwajibkan, misalnya 14 untuk A_14 atau 3 untuk B_3.

    Returns
    -------
    np.ndarray
        Matriks numerik dengan skor pada rentang 0 sampai 5.
    """
    if isinstance(data, pd.DataFrame):
        values = data.to_numpy(dtype=float)
    else:
        values = np.asarray(data, dtype=float)

    if values.ndim != 2:
        raise ValueError(f"{name} harus berupa data 2 dimensi.")

    if expected_columns is not None and values.shape[1] != expected_columns:
        raise ValueError(
            f"{name} harus memiliki {expected_columns} fitur; "
            f"ditemukan {values.shape[1]}."
        )

    # Eksperimen membandingkan k=2..6, sehingga minimal perlu enam responden.
    if values.shape[0] < 6:
        raise ValueError(
            "Minimal diperlukan 6 responden untuk eksperimen k=2..6."
        )

    if not np.isfinite(values).all():
        raise ValueError(f"{name} mengandung missing value atau nilai tak hingga.")

    if np.any(values < 0) or np.any(values > 5):
        raise ValueError(
            f"{name} harus berada pada rentang skor MHC-SF 0 sampai 5."
        )

    return values


def prepare_experiment_data(
    data_14: Any,
    data_3: Any,
) -> dict[str, np.ndarray]:
    """Memvalidasi A_14 dan B_3 serta memastikan baris responden selaras.

    A_14 berisi 14 skor butir MHC-SF, sedangkan B_3 berisi rata-rata skor
    Emotional, Social, dan Psychological. Kedua representasi harus berasal
    dari responden yang sama dan memiliki urutan baris yang sama.
    """
    X_14 = _to_numpy(
        data_14,
        name="A_14",
        expected_columns=ITEM_FEATURE_COUNT,
    )
    X_3 = _to_numpy(data_3, name="B_3", expected_columns=3)

    if len(X_14) != len(X_3):
        raise ValueError(
            "A_14 dan B_3 harus memiliki jumlah responden yang sama."
        )

    return {"A_14": X_14, "B_3": X_3}


def prepare_features(data: Any) -> np.ndarray:
    """Memvalidasi matriks tiga dimensi untuk model Two-Layer.

    Jika input berupa DataFrame, nama dan urutan kolom wajib tepat sama
    dengan FEATURE_COLUMNS agar model tidak menerima fitur yang tertukar.
    """
    if isinstance(data, pd.DataFrame):
        if list(data.columns) != FEATURE_COLUMNS:
            raise ValueError(
                f"Urutan kolom harus tepat: {FEATURE_COLUMNS}. "
                f"Ditemukan: {list(data.columns)}"
            )

    return _to_numpy(data, name="B_3", expected_columns=3)


def transform_relative_features(X: Any) -> np.ndarray:
    """Mengubah skor absolut menjadi pola relatif untuk setiap responden.

    Untuk setiap responden, rata-rata tiga dimensi dikurangkan dari masing-
    masing skor dimensi. Nilai positif berarti dimensi tersebut relatif lebih
    tinggi daripada rata-rata pribadi responden; nilai negatif berarti relatif
    lebih rendah.

    Transformasi ini tidak menunjukkan tingkat kesejahteraan absolut.
    """
    values = prepare_features(X)
    respondent_means = values.mean(axis=1, keepdims=True)
    return values - respondent_means


# ---------------------------------------------------------------------------
# Estimator kandidat
# Parameter utama mengikuti eksperimen notebook.
# ---------------------------------------------------------------------------

def _require_kmedoids() -> None:
    """Memastikan dependensi K-Medoids tersedia sebelum estimator dipakai."""
    if kmedoids is None:
        raise ImportError(
            "Library 'kmedoids' belum tersedia. Install di ENV_001 dengan: "
            "pip install kmedoids"
        ) from _KMEDOIDS_IMPORT_ERROR


def _fit_candidate(
    algorithm: str,
    X: np.ndarray,
    k: int,
    *,
    seed: int = RANDOM_STATE,
):
    """Melatih satu algoritma kandidat dan mengembalikan model serta label.

    K-Medoids menggunakan matriks jarak Euclidean karena estimator dipanggil
    dengan metric='precomputed'. Agglomerative menggunakan Ward linkage.
    """
    if algorithm == "K-Means":
        model = KMeans(
            n_clusters=k,
            random_state=seed,
            n_init=N_INIT,
        )
        labels = model.fit_predict(X)
        return model, labels

    if algorithm == "Agglomerative":
        model = AgglomerativeClustering(
            n_clusters=k,
            metric="euclidean",
            linkage="ward",
        )
        labels = model.fit_predict(X)
        return model, labels

    if algorithm == "K-Medoids":
        _require_kmedoids()
        from sklearn.metrics.pairwise import euclidean_distances

        distance_matrix = euclidean_distances(X)
        model = kmedoids.KMedoids(
            n_clusters=k,
            metric="precomputed",
            method="fasterpam",
            init="build",
            max_iter=300,
            random_state=seed,
        )
        labels = model.fit_predict(distance_matrix)
        return model, labels

    raise ValueError(f"Algoritma tidak dikenal: {algorithm}")


def _internal_metrics(
    X: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float]:
    """Menghitung tiga metrik internal; nilai tidak valid ditandai NaN.

    Silhouette dan Calinski-Harabasz semakin baik ketika nilainya lebih besar.
    Davies-Bouldin semakin baik ketika nilainya lebih kecil.
    Metrik tidak dapat dihitung secara bermakna jika hanya ada satu cluster
    atau setiap observasi menjadi cluster tersendiri.
    """
    unique_labels = np.unique(labels)

    if len(unique_labels) < 2 or len(unique_labels) >= len(labels):
        return {
            "silhouette": np.nan,
            "davies_bouldin": np.nan,
            "calinski_harabasz": np.nan,
        }

    return {
        "silhouette": float(silhouette_score(X, labels, metric="euclidean")),
        "davies_bouldin": float(davies_bouldin_score(X, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
    }


# ---------------------------------------------------------------------------
# Evaluasi stabilitas: B_3, k=2, subsampling berulang, pairwise ARI
# ---------------------------------------------------------------------------

def evaluate_algorithm_stability(
    X: Any,
    *,
    n_runs: int = N_STABILITY_RUNS,
    sample_fraction: float = STABILITY_SAMPLE_FRACTION,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """Mengukur konsistensi hasil cluster pada subsample yang saling tumpang tindih.

    Pada setiap pengulangan, sebagian responden dipilih tanpa pengembalian.
    Label dari dua pengulangan dibandingkan hanya pada responden yang muncul
    di kedua subsample. Adjusted Rand Index (ARI) mengukur kesesuaian partisi
    tanpa bergantung pada nomor label cluster.

    Hasil akhir berisi ringkasan seluruh perbandingan berpasangan untuk
    masing-masing algoritma.
    """
    values = prepare_features(X)

    if n_runs < 2:
        raise ValueError("n_runs minimal 2 agar pairwise ARI dapat dihitung.")

    if not 0 < sample_fraction <= 1:
        raise ValueError("sample_fraction harus lebih besar dari 0 dan <= 1.")

    sample_size = int(sample_fraction * len(values))
    if sample_size < 2:
        raise ValueError("Ukuran subsample terlalu kecil untuk uji stabilitas.")

    rng = np.random.default_rng(random_state)
    runs: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {
        name: [] for name in ALGORITHM_ORDER
    }

    for run in range(n_runs):
        indices = np.sort(
            rng.choice(len(values), size=sample_size, replace=False)
        )
        X_sample = values[indices]

        for algorithm in ALGORITHM_ORDER:
            _, labels = _fit_candidate(
                algorithm,
                X_sample,
                2,
                seed=RANDOM_STATE + run,
            )
            runs[algorithm].append((indices.copy(), labels.copy()))

    rows = []

    for algorithm, algorithm_runs in runs.items():
        ari_scores = []

        for (idx_a, labels_a), (idx_b, labels_b) in combinations(
            algorithm_runs,
            2,
        ):
            # Temukan responden yang muncul pada kedua subsample, lalu ambil
            # posisi labelnya dari masing-masing hasil clustering.
            _, pos_a, pos_b = np.intersect1d(
                idx_a,
                idx_b,
                return_indices=True,
            )

            ari_scores.append(
                adjusted_rand_score(labels_a[pos_a], labels_b[pos_b])
            )

        rows.append({
            "algorithm": algorithm,
            "mean_ari": float(np.mean(ari_scores)),
            "std_ari": float(np.std(ari_scores)),
            "min_ari": float(np.min(ari_scores)),
            "max_ari": float(np.max(ari_scores)),
            "n_pairwise_comparisons": len(ari_scores),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Pemilihan algoritma otomatis berbasis mean-rank
# ---------------------------------------------------------------------------

def _rank_candidates(selection_df: pd.DataFrame) -> pd.DataFrame:
    """Memberi peringkat kandidat pada setiap metrik dan menghitung mean-rank.

    Peringkat 1 adalah yang terbaik. Metrik yang tidak tersedia (NaN), misalnya
    stabilitas ketika run_stability=False, diabaikan dalam perhitungan mean.
    Semua metrik yang tersedia diberi bobot sama.
    """
    result = selection_df.copy()

    result["rank_silhouette"] = result["silhouette"].rank(
        ascending=False,
        method="average",
    )
    result["rank_davies_bouldin"] = result["davies_bouldin"].rank(
        ascending=True,
        method="average",
    )
    result["rank_calinski_harabasz"] = result["calinski_harabasz"].rank(
        ascending=False,
        method="average",
    )
    result["rank_stability"] = result["mean_ari"].rank(
        ascending=False,
        method="average",
    )

    rank_columns = [
        "rank_silhouette",
        "rank_davies_bouldin",
        "rank_calinski_harabasz",
        "rank_stability",
    ]

    result["mean_rank"] = result[rank_columns].mean(axis=1, skipna=True)
    result["selection_score"] = 1.0 / result["mean_rank"]
    result["selected"] = False

    valid_rows = result["mean_rank"].dropna()
    if not valid_rows.empty:
        winner_index = valid_rows.idxmin()
        result.loc[winner_index, "selected"] = True

    return result.sort_values(
        ["selected", "mean_rank"],
        ascending=[False, True],
        na_position="last",
    ).reset_index(drop=True)


def run_model_selection(
    data_14: Any,
    data_3: Any,
    *,
    k_values=K_RANGE,
    run_stability: bool = True,
) -> dict[str, Any]:
    """Menjalankan eksperimen kandidat dan memilih konfigurasi B_3, k=2.

    Semua kombinasi algoritma, representasi, dan nilai k disimpan pada
    experiment_results. Pemilihan otomatis dibatasi pada B_3, k=2 karena
    konfigurasi tersebut menjadi basis model Two-Layer pada notebook.

    Jika run_stability=False, pemeringkatan dilakukan berdasarkan tiga metrik
    internal saja. Kondisi ini berguna untuk pengujian cepat, tetapi bukan
    konfigurasi evaluasi lengkap yang direkomendasikan untuk seleksi final.
    """
    datasets = prepare_experiment_data(data_14, data_3)
    k_values = tuple(int(k) for k in k_values)

    if not k_values or any(
        k < 2 or k >= len(datasets["B_3"]) for k in k_values
    ):
        raise ValueError(
            "Setiap nilai k harus >=2 dan lebih kecil dari jumlah responden."
        )

    candidate_models: dict[tuple[str, str, int], Any] = {}
    candidate_labels: dict[tuple[str, str, int], np.ndarray] = {}
    rows = []

    for algorithm in ALGORITHM_ORDER:
        for representation in REPRESENTATIONS:
            X = datasets[representation]

            for k in k_values:
                model, labels = _fit_candidate(algorithm, X, k)
                metrics = _internal_metrics(X, labels)
                key = (algorithm, representation, k)

                candidate_models[key] = model
                candidate_labels[key] = labels

                rows.append({
                    "algorithm": algorithm,
                    "representation": representation,
                    "k": k,
                    **metrics,
                    "inertia_or_objective": float(
                        getattr(model, "inertia_", np.nan)
                    ),
                    "cluster_count": int(len(np.unique(labels))),
                })

    experiment_df = pd.DataFrame(rows)

    if run_stability:
        stability_df = evaluate_algorithm_stability(datasets["B_3"])
    else:
        stability_df = pd.DataFrame({
            "algorithm": ALGORITHM_ORDER,
            "mean_ari": [np.nan] * len(ALGORITHM_ORDER),
            "std_ari": [np.nan] * len(ALGORITHM_ORDER),
            "min_ari": [np.nan] * len(ALGORITHM_ORDER),
            "max_ari": [np.nan] * len(ALGORITHM_ORDER),
            "n_pairwise_comparisons": [0] * len(ALGORITHM_ORDER),
        })

    # Pemilihan dilakukan pada konfigurasi yang menjadi basis model final.
    selection_df = (
        experiment_df.query("representation == 'B_3' and k == 2")
        .merge(stability_df, on="algorithm", how="left")
    )
    ranked_selection = _rank_candidates(selection_df)

    selected_rows = ranked_selection.loc[ranked_selection["selected"]]
    if selected_rows.empty:
        raise RuntimeError(
            "Tidak ada kandidat yang dapat dipilih. Periksa hasil metrik "
            "dan jumlah cluster yang terbentuk."
        )

    selected_row = selected_rows.iloc[0]
    selected_key = (str(selected_row["algorithm"]), "B_3", 2)

    return {
        "experiment_results": experiment_df,
        "stability_results": stability_df,
        "selection_results": ranked_selection,
        "selected_algorithm": selected_key[0],
        "selected_representation": selected_key[1],
        "selected_k": selected_key[2],
        "selected_model": candidate_models[selected_key],
        "selected_labels": candidate_labels[selected_key],
        "candidate_models": candidate_models,
        "candidate_labels": candidate_labels,
        "feature_data": datasets,
        "selection_method": (
            "Mean rank berbobot sama: Silhouette (descending), "
            "Davies-Bouldin (ascending), Calinski-Harabasz (descending), "
            "dan stability mean ARI (descending). "
            "Cakupan seleksi: B_3, k=2."
        ),
    }


# ---------------------------------------------------------------------------
# Interpretasi semantik setelah clustering
# ---------------------------------------------------------------------------

def interpret_overall_clusters(model: KMeans) -> dict[int, str]:
    """Memberi makna Tinggi/Rendah berdasarkan rata-rata centroid Overall.

    K-Means hanya menghasilkan nomor cluster. Nomor tersebut bukan label
    Tinggi/Rendah bawaan model. Setelah model dilatih, centroid dengan rata-
    rata tiga dimensi lebih tinggi diberi makna Tinggi, dan sebaliknya.
    """
    centers = np.asarray(model.cluster_centers_, dtype=float)

    if centers.shape != (2, 3):
        raise ValueError("Overall model harus memiliki 2 cluster dan 3 fitur.")

    center_means = centers.mean(axis=1)
    high_id = int(np.argmax(center_means))
    low_id = int(np.argmin(center_means))

    if high_id == low_id:
        raise ValueError("Centroid Overall tidak dapat dibedakan.")

    return {high_id: "Tinggi", low_id: "Rendah"}


def interpret_pattern_clusters(
    model: KMeans,
    *,
    min_gap: float = PATTERN_MIN_GAP,
) -> dict[int, str]:
    """Menafsirkan pola relatif berdasarkan ketiga dimensi centroid.

    Untuk setiap centroid:
    1. Urutkan tiga nilai relatif dari yang paling rendah.
    2. Hitung selisih antara nilai terendah dan nilai terendah kedua.
    3. Jika selisih >= min_gap, dimensi terendah diberi label
       '... Relatif Rendah'.
    4. Jika selisih < min_gap, centroid diberi label 'Seimbang'.

    Dengan demikian, fungsi tidak lagi mengunci interpretasi pada Social.
    Emotional, Social, maupun Psychological dapat menjadi dimensi relatif
    terendah, bergantung pada centroid hasil pelatihan.

    min_gap adalah ambang interpretasi pada skala skor dimensi, bukan batas
    diagnosis. Nilainya harus ditinjau melalui analisis sensitivitas dan
    validasi substantif sebelum digunakan sebagai aturan final.
    """
    centers = np.asarray(model.cluster_centers_, dtype=float)

    if centers.shape != (2, 3):
        raise ValueError("Pattern model harus memiliki 2 cluster dan 3 fitur.")

    if not np.isfinite(centers).all():
        raise ValueError("Centroid Pattern mengandung nilai tidak valid.")

    if min_gap < 0:
        raise ValueError("min_gap tidak boleh bernilai negatif.")

    label_map: dict[int, str] = {}

    for cluster_id, center in enumerate(centers):
        # Indeks fitur diurutkan dari nilai centroid relatif paling rendah.
        sorted_indices = np.argsort(center)
        lowest_index = int(sorted_indices[0])
        second_lowest_index = int(sorted_indices[1])

        # Gap positif yang besar menunjukkan satu dimensi lebih rendah
        # dibandingkan dua dimensi lainnya pada centroid cluster tersebut.
        gap = float(center[second_lowest_index] - center[lowest_index])

        if gap >= min_gap:
            dimension_name = FEATURE_COLUMNS[lowest_index]
            label_map[cluster_id] = PATTERN_DIMENSION_LABELS[dimension_name]
        else:
            label_map[cluster_id] = "Seimbang"

    return label_map


def calculate_recommendation_thresholds(data: Any) -> dict[str, float]:
    """Menghitung Q1 dengan pembagian holdout yang sama seperti notebook.

    Data dibagi dengan test_size=0.2 dan random_state=42. Kuartil pertama
    dihitung hanya dari bagian training, mengikuti alur notebook (cell 57
    dan 68), bukan dari keseluruhan data.
    """
    X = prepare_features(data)

    X_train, _ = train_test_split(
        X,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    thresholds = pd.DataFrame(
        X_train,
        columns=FEATURE_COLUMNS,
    ).quantile(0.25)

    return {
        column: float(thresholds[column])
        for column in FEATURE_COLUMNS
    }


# ---------------------------------------------------------------------------
# Finalisasi model Two-Layer K-Means
# ---------------------------------------------------------------------------

def train_two_layer_model(data: Any) -> dict[str, Any]:
    """Melatih model Overall dan Relative Pattern sesuai model final notebook.

    Layer 1 (Overall):
        K-Means k=2 pada skor absolut Emotional, Social, Psychological.

    Layer 2 (Relative Pattern):
        K-Means k=2 pada skor yang sudah dipusatkan per responden.

    Fungsi ini sengaja tetap menggunakan K-Means karena model final pada
    notebook menggunakan K-Means. Fungsi ini bukan pengganti otomatis bagi
    K-Medoids atau Agglomerative tanpa rancangan inferensi dan evaluasi baru.
    """
    X = prepare_features(data)
    X_relative = transform_relative_features(X)

    overall_model = KMeans(
        n_clusters=2,
        random_state=RANDOM_STATE,
        n_init=N_INIT,
    )
    overall_labels = overall_model.fit_predict(X)

    pattern_model = KMeans(
        n_clusters=2,
        random_state=RANDOM_STATE,
        n_init=N_INIT,
    )
    pattern_labels = pattern_model.fit_predict(X_relative)

    overall_label_map = interpret_overall_clusters(overall_model)
    pattern_label_map = interpret_pattern_clusters(pattern_model)
    q1_thresholds = calculate_recommendation_thresholds(X)

    package = {
        "model_version": None,
        "created_at": datetime.now().isoformat(),
        "overall_model": overall_model,
        "pattern_model": pattern_model,
        "feature_columns": FEATURE_COLUMNS.copy(),
        "overall_label_map": overall_label_map,
        "pattern_label_map": pattern_label_map,
        "q1_thresholds": q1_thresholds,
        "training_info": {
            "dataset_size": int(len(X)),
            "feature_count": int(X.shape[1]),
            "algorithms": {
                "overall": "KMeans",
                "pattern": "KMeans",
            },
            "n_clusters": {
                "overall": 2,
                "pattern": 2,
            },
            "random_state": RANDOM_STATE,
            "n_init": N_INIT,
            "architecture": "Two-Layer K-Means",
            "pattern_interpretation_min_gap": PATTERN_MIN_GAP,
        },
    }

    return {
        "model_package": package,
        "overall_labels": overall_labels,
        "pattern_labels": pattern_labels,
        "features": X,
        "relative_features": X_relative,
    }


def train_candidate_model(
    data_14: Any,
    data_3: Any,
) -> dict[str, Any]:
    """Menjalankan seleksi algoritma dan menyiapkan Two-Layer jika K-Means menang.

    Implementasi Two-Layer yang tersedia saat ini adalah K-Means sesuai
    notebook. Jika K-Medoids atau Agglomerative terpilih, fungsi tidak
    menggantinya diam-diam dengan K-Means. Hasil seleksi dikembalikan untuk
    ditinjau dan desain inferensi Two-Layer algoritma tersebut perlu dibuat
    serta dievaluasi terlebih dahulu.
    """
    selection = run_model_selection(data_14, data_3)

    if selection["selected_algorithm"] != "K-Means":
        return {
            "selection": selection,
            "two_layer_training": None,
            "status": (
                "selected_algorithm_requires_two_layer_inference_design"
            ),
        }

    two_layer = train_two_layer_model(data_3)
    package = two_layer["model_package"]

    package["training_info"]["selection"] = {
        "selected_algorithm": selection["selected_algorithm"],
        "selected_representation": selection["selected_representation"],
        "selected_k": selection["selected_k"],
        "selection_method": selection["selection_method"],
    }

    return {
        "selection": selection,
        "two_layer_training": two_layer,
        "status": "ready_for_model_evaluation_and_registry",
    }


def train_two_layer_model_legacy(data: Any) -> dict[str, Any]:
    """Nama kompatibilitas untuk pemanggil prototype versi sebelumnya."""
    return train_two_layer_model(data)
