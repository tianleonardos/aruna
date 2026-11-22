"""Modul Evaluasi Model dan Analisis Stabilitas ARUNA.

Bertanggung jawab untuk:
1. Perhitungan metrik evaluasi internal (Silhouette, Davies-Bouldin, Calinski-Harabasz).
2. Analisis stabilitas cluster berbasis subsampling berulang dan pairwise ARI.
3. Perbandingan model Two-Layer Clustering vs Direct K-Means K=4.
4. Evaluasi holdout validation (80% Train, 20% Test).
5. Pembentukan ringkasan statistik karakteristik profil dan centroid.
"""

from __future__ import annotations

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

FEATURE_COLUMNS = ["Emotional", "Social", "Psychological"]
RANDOM_STATE = 42


def compute_internal_metrics(X: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    """Menghitung tiga metrik pemisahan dan kekompakan cluster internal.

    Parameters
    ----------
    X : np.ndarray
        Matriks fitur numerik (misalnya representasi B_3).
    labels : np.ndarray
        Array label cluster hasil pemodelan.

    Returns
    -------
    dict[str, float]
        Silhouette Score, Davies-Bouldin Index, dan Calinski-Harabasz Index.
    """
    unique_labels = np.unique(labels)

    if len(unique_labels) < 2 or len(unique_labels) >= len(labels):
        return {
            "silhouette": float("nan"),
            "davies_bouldin": float("nan"),
            "calinski_harabasz": float("nan"),
        }

    return {
        "silhouette": float(silhouette_score(X, labels, metric="euclidean")),
        "davies_bouldin": float(davies_bouldin_score(X, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
    }


def evaluate_subsampling_stability(
    X: np.ndarray,
    algorithm: str = "K-Means",
    k: int = 2,
    *,
    n_runs: int = 30,
    sample_fraction: float = 0.8,
    random_state: int = RANDOM_STATE,
) -> dict[str, float]:
    """Mengukur konsistensi pengelompokan menggunakan subsampling dan pairwise ARI.

    Sesuai Bab 4.3 Master Technical Documentation:
    Dilakukan pengujian subsampling berulang (default 30 kali) pada 80% data,
    kemudian menghitung Adjusted Rand Index (ARI) antar pasangan subsample.
    """
    if len(X) < 10:
        raise ValueError("Jumlah sampel terlalu sedikit untuk evaluasi stabilitas.")

    sample_size = int(sample_fraction * len(X))
    rng = np.random.default_rng(random_state)
    runs: list[tuple[np.ndarray, np.ndarray]] = []

    for run_idx in range(n_runs):
        indices = np.sort(rng.choice(len(X), size=sample_size, replace=False))
        X_sub = X[indices]

        if algorithm == "K-Means":
            model = KMeans(
                n_clusters=k,
                random_state=random_state + run_idx,
                n_init=20,
            )
            labels = model.fit_predict(X_sub)
        elif algorithm == "Agglomerative":
            model = AgglomerativeClustering(
                n_clusters=k,
                metric="euclidean",
                linkage="ward",
            )
            labels = model.fit_predict(X_sub)
        else:
            raise ValueError(f"Algoritma {algorithm} belum didukung pada stabilitas ini.")

        runs.append((indices, labels))

    pairwise_ari: list[float] = []

    for (idx_a, lbl_a), (idx_b, lbl_b) in combinations(runs, 2):
        _, pos_a, pos_b = np.intersect1d(idx_a, idx_b, return_indices=True)
        if len(pos_a) > 2:
            score = adjusted_rand_score(lbl_a[pos_a], lbl_b[pos_b])
            pairwise_ari.append(score)

    if not pairwise_ari:
        return {
            "mean_ari": float("nan"),
            "std_ari": float("nan"),
            "min_ari": float("nan"),
            "max_ari": float("nan"),
        }

    return {
        "mean_ari": float(np.mean(pairwise_ari)),
        "std_ari": float(np.std(pairwise_ari)),
        "min_ari": float(np.min(pairwise_ari)),
        "max_ari": float(np.max(pairwise_ari)),
        "n_comparisons": len(pairwise_ari),
    }


def compare_two_layer_vs_direct_kmeans(
    X: np.ndarray,
    *,
    n_stability_runs: int = 30,
) -> pd.DataFrame:
    """Membandingkan Two-Layer Clustering vs Direct K-Means K=4.

    Mendokumentasikan temuan penting Bab 6.1 Master Technical Documentation:
    Direct K-Means K=4 memperoleh metrik pemisahan internal yang lebih baik,
    namun Two-Layer menghasilkan Mean ARI yang jauh lebih tinggi (stabilitas
    lebih tinggi) dan struktur interpretasi yang jelas.
    """
    # 1. Direct K-Means K=4
    direct_model = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=20)
    direct_labels = direct_model.fit_predict(X)
    direct_metrics = compute_internal_metrics(X, direct_labels)
    direct_stability = evaluate_subsampling_stability(
        X, algorithm="K-Means", k=4, n_runs=n_stability_runs
    )

    # 2. Two-Layer Clustering (Layer 1 Overall + Layer 2 Relative Pattern)
    overall_model = KMeans(n_clusters=2, random_state=RANDOM_STATE, n_init=20)
    overall_labels = overall_model.fit_predict(X)

    respondent_means = X.mean(axis=1, keepdims=True)
    X_rel = X - respondent_means
    pattern_model = KMeans(n_clusters=2, random_state=RANDOM_STATE, n_init=20)
    pattern_labels = pattern_model.fit_predict(X_rel)

    # Gabungan 4 profil
    two_layer_cluster_ids = overall_labels * 2 + pattern_labels
    two_layer_metrics = compute_internal_metrics(X, two_layer_cluster_ids)

    # Stabilitas Two-Layer
    rng = np.random.default_rng(RANDOM_STATE)
    sample_size = int(0.8 * len(X))
    two_layer_runs = []

    for r in range(n_stability_runs):
        idx = np.sort(rng.choice(len(X), size=sample_size, replace=False))
        sub_X = X[idx]
        sub_rel = sub_X - sub_X.mean(axis=1, keepdims=True)

        km_o = KMeans(n_clusters=2, random_state=RANDOM_STATE + r, n_init=20)
        lbl_o = km_o.fit_predict(sub_X)

        km_p = KMeans(n_clusters=2, random_state=RANDOM_STATE + r, n_init=20)
        lbl_p = km_p.fit_predict(sub_rel)

        combined = lbl_o * 2 + lbl_p
        two_layer_runs.append((idx, combined))

    two_layer_ari = []
    for (ia, la), (ib, lb) in combinations(two_layer_runs, 2):
        _, pa, pb = np.intersect1d(ia, ib, return_indices=True)
        if len(pa) > 2:
            two_layer_ari.append(adjusted_rand_score(la[pa], lb[pb]))

    rows = [
        {
            "Pendekatan": "Two-Layer Clustering",
            "Silhouette": two_layer_metrics["silhouette"],
            "Davies-Bouldin": two_layer_metrics["davies_bouldin"],
            "Calinski-Harabasz": two_layer_metrics["calinski_harabasz"],
            "Mean ARI": float(np.mean(two_layer_ari)),
            "Std ARI": float(np.std(two_layer_ari)),
            "Keunggulan": "Stabilitas sangat tinggi & interpretasi 2x2 terstruktur",
        },
        {
            "Pendekatan": "Direct K-Means K=4",
            "Silhouette": direct_metrics["silhouette"],
            "Davies-Bouldin": direct_metrics["davies_bouldin"],
            "Calinski-Harabasz": direct_metrics["calinski_harabasz"],
            "Mean ARI": direct_stability["mean_ari"],
            "Std ARI": direct_stability["std_ari"],
            "Keunggulan": "Pemisahan matematis internal sedikit lebih baik",
        },
    ]

    return pd.DataFrame(rows)


def evaluate_holdout_validation(
    X: np.ndarray,
    *,
    test_size: float = 0.2,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    """Menjalankan evaluasi holdout validation (80% Train, 20% Test).

    Menguji apakah model yang dilatih pada training set mampu memprediksi
    data baru (test set) secara konsisten sesuai Bab 6.2 Master Document.
    """
    X_train, X_test = train_test_split(
        X, test_size=test_size, random_state=random_state
    )

    # Latih model pada train set
    km_overall = KMeans(n_clusters=2, random_state=random_state, n_init=20)
    train_overall_labels = km_overall.fit_predict(X_train)

    train_rel = X_train - X_train.mean(axis=1, keepdims=True)
    km_pattern = KMeans(n_clusters=2, random_state=random_state, n_init=20)
    train_pattern_labels = km_pattern.fit_predict(train_rel)

    # Prediksi data testing
    test_overall_labels = km_overall.predict(X_test)
    test_rel = X_test - X_test.mean(axis=1, keepdims=True)
    test_pattern_labels = km_pattern.predict(test_rel)

    # Metrik train
    train_overall_metrics = compute_internal_metrics(X_train, train_overall_labels)
    train_pattern_metrics = compute_internal_metrics(train_rel, train_pattern_labels)

    # Metrik test
    test_overall_metrics = compute_internal_metrics(X_test, test_overall_labels)
    test_pattern_metrics = compute_internal_metrics(test_rel, test_pattern_labels)

    return {
        "train_size": len(X_train),
        "test_size": len(X_test),
        "overall_layer": {
            "train": train_overall_metrics,
            "test": test_overall_metrics,
        },
        "pattern_layer": {
            "train": train_pattern_metrics,
            "test": test_pattern_metrics,
        },
        "test_overall_labels": test_overall_labels,
        "test_pattern_labels": test_pattern_labels,
    }


def compute_profile_summary_table(
    features_3: np.ndarray,
    profile_names: list[str],
) -> pd.DataFrame:
    """Menghitung rata-rata dan deviasi standar skor dimensi untuk setiap profil.

    Parameters
    ----------
    features_3 : np.ndarray
        Skor dimensi [Emotional, Social, Psychological] (332 x 3).
    profile_names : list[str]
        Nama profil gabungan untuk masing-masing responden.

    Returns
    -------
    pd.DataFrame
        Tabel ringkasan karakteristik psikososial tiap profil.
    """
    df = pd.DataFrame(features_3, columns=FEATURE_COLUMNS)
    df["Profil"] = profile_names

    summary = (
        df.groupby("Profil")
        .agg(
            Jumlah=("Emotional", "count"),
            Emotional=("Emotional", "mean"),
            Social=("Social", "mean"),
            Psychological=("Psychological", "mean"),
        )
        .reset_index()
    )

    summary["Persentase"] = (summary["Jumlah"] / len(df)) * 100
    return summary
