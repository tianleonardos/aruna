import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np

from src.theme import apply_theme, get_vector, get_logo_base64
from src.preprocessing import preprocess_mhcsf_dataset
from src.evaluation import (
    compute_internal_metrics,
    evaluate_holdout_validation,
    compare_two_layer_vs_direct_kmeans,
)

# Cek autentikasi dan peran admin
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# Terapkan styling & kontrol visibilitas sidebar
apply_theme(hide_sidebar=not is_admin)

if not is_admin:
    st.warning("⚠️ Akses Terbatas: Halaman ini hanya dapat diakses oleh Administrator & Peneliti.")
    st.info("Silakan login menggunakan akun Administrator di Beranda Utama.")
    st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda Utama", icon="🌱")
    st.stop()

# Tombol navigasi kembali ke Admin Dashboard
st.page_link("pages/1_Admin_Dashboard.py", label="⬅️ Kembali ke Admin Dashboard", icon="🏠")

logo_data_uri = get_logo_base64()
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
        <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
        <div>
            <span class="aruna-badge">Penelitian & Validasi</span>
            <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("Evaluasi & Perbandingan Model")
st.caption(
    "Analisis kualitas pemisahan cluster, stabilitas subsampling, "
    "holdout validation, dan pembenaran metodologis Two-Layer Clustering."
)
st.divider()

# ===========================================================================
# NAVIGASI TAB EVALUASI
# ===========================================================================

tab_algo, tab_twolayer, tab_holdout, tab_profiles = st.tabs([
    "📊 Perbandingan 3 Algoritma",
    "⚖️ Two-Layer vs Direct K-Means",
    "🧪 Holdout Validation (80/20)",
    "🎯 Karakteristik 4 Profil Aruna",
])


# ===========================================================================
# TAB 1: PERBANDINGAN 3 ALGORITMA
# ===========================================================================
with tab_algo:
    st.subheader("1. Evaluasi Tiga Algoritma Kandidat")
    st.write(
        "Notebook final membandingkan tiga algoritma clustering pada representasi $B_3$ "
        "(skor rata-rata Emotional, Social, dan Psychological) dengan $K=2$ menggunakan 30 kali subsampling."
    )

    algo_comparison_data = {
        "Algoritma": ["K-Means", "K-Medoids", "Agglomerative"],
        "Silhouette Score (↑)": [0.4292, 0.4290, 0.3942],
        "Davies-Bouldin Index (↓)": [0.8497, 0.8501, 0.8532],
        "Calinski-Harabasz Index (↑)": [391.78, 391.69, 305.87],
        "Mean ARI Stabilitas (↑)": [0.9088, 0.9008, 0.4800],
    }
    df_algo = pd.DataFrame(algo_comparison_data)

    st.dataframe(df_algo, use_container_width=True)

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Silhouette Score (Kekompakan & Pemisahan):**")
        st.bar_chart(df_algo.set_index("Algoritma")["Silhouette Score (↑)"])

    with col_chart2:
        st.markdown("**Stabilitas Subsampling (Mean ARI 30 Runs):**")
        st.bar_chart(df_algo.set_index("Algoritma")["Mean ARI Stabilitas (↑)"])

    st.success(
        "💡 **Keputusan Ilmiah:** K-Means dan K-Medoids memberikan kualitas yang hampir seimbang, "
        "namun K-Means memiliki nilai evaluasi internal sedikit lebih baik dan stabilitas subsampling tertinggi (0.9088). "
        "Agglomerative memiliki stabilitas yang jauh lebih rendah (0.4800). Oleh karena itu, K-Means dipilih sebagai algoritma utama."
    )


# ===========================================================================
# TAB 2: TWO-LAYER VS DIRECT K-MEANS K=4
# ===========================================================================
with tab_twolayer:
    st.subheader("2. Pembenaran Arsitektur: Two-Layer vs Direct K-Means (K=4)")
    st.write(
        "Penelitian membandingkan apakah pemetaan 4 profil lebih baik dilakukan langsung "
        "menggunakan Direct K-Means ($K=4$) atau menggunakan arsitektur Two-Layer ($2 \\times 2$)."
    )

    twolayer_comparison = {
        "Metrik Evaluasi": [
            "Silhouette Score (↑)",
            "Davies-Bouldin Index (↓)",
            "Calinski-Harabasz Index (↑)",
            "Mean ARI Stabilitas (↑)",
            "Std ARI Stabilitas (↓)",
        ],
        "Two-Layer Clustering": [0.1850, 1.7801, 193.45, 0.9115, 0.0597],
        "Direct K-Means (K=4)": [0.2923, 1.1068, 303.40, 0.6806, 0.1851],
    }
    df_tl = pd.DataFrame(twolayer_comparison)
    st.dataframe(df_tl.set_index("Metrik Evaluasi"), use_container_width=True)

    col_tl1, col_tl2 = st.columns(2)
    with col_tl1:
        st.metric("Stabilitas Two-Layer (ARI)", "0.9115", delta="+0.2309 vs Direct K-Means")
    with col_tl2:
        st.metric("Variasi Stabilitas (Std ARI)", "0.0597", delta="-0.1254 (Lebih Konsisten)", delta_color="inverse")

    st.warning(
        "⚠️ **Keterbatasan & Transparansi Akademik:**  \n"
        "Direct K-Means $K=4$ memang unggul pada metrik geometris internal (Silhouette 0.29 vs 0.18).  \n"
        "**Namun, Two-Layer Clustering dipilih karena:**  \n"
        "1. **Stabilitas Partisi Jauh Lebih Tinggi:** Mean ARI mencapai **0.9115** berbanding 0.6806 pada pengujian subsampling berulang.  \n"
        "2. **Interpretabilitas Nyata:** Memisahkan *tingkat kesejahteraan keseluruhan* dari *komposisi relatif dimensi*, "
        "sehingga menghasilkan profil yang dapat dipahami dan ditindaklanjuti secara psikososial."
    )


# ===========================================================================
# TAB 3: HOLDOUT VALIDATION (80% TRAIN, 20% TEST)
# ===========================================================================
with tab_holdout:
    st.subheader("3. Validasi Holdout (80% Training, 20% Testing)")
    st.write(
        "Dataset 332 responden dibagi menjadi 265 data training (80%) dan 67 data testing (20%) "
        "dengan random state 42 untuk menguji kemampuan generalisasi inferensi model."
    )

    holdout_summary = {
        "Lapisan Model": ["Layer 1: Overall Clustering", "Layer 2: Relative Pattern Clustering"],
        "Silhouette (Train)": [0.4685, 0.3845],
        "Davies-Bouldin (Train)": [0.7701, 0.9705],
        "Calinski-Harabasz (Train)": [89.64, 50.05],
    }
    st.dataframe(pd.DataFrame(holdout_summary), use_container_width=True)

    st.markdown("**Distribusi Kombinasi Profil pada Data Testing (67 Responden):**")
    test_dist = {
        "Profil Hasil Prediksi": [
            "Tinggi - Sosial Relatif Rendah",
            "Rendah - Seimbang",
            "Tinggi - Seimbang",
            "Rendah - Sosial Relatif Rendah",
        ],
        "Jumlah Responden": [20, 19, 15, 13],
        "Persentase": ["29.85%", "28.36%", "22.39%", "19.40%"],
    }
    st.dataframe(pd.DataFrame(test_dist), use_container_width=True)

    st.info(
        "📌 **Catatan Validasi:** Model terbukti dapat mengklasifikasikan data pengujian secara konsisten. "
        "Namun, karena dataset berasal dari universitas di Kanada, hasil ini adalah validasi internal dan "
        "masih membutuhkan penelitian eksternal lanjutan jika ingin digeneralisasi ke mahasiswa Indonesia."
    )


# ===========================================================================
# TAB 4: KARAKTERISTIK 4 PROFIL ARUNA
# ===========================================================================
with tab_profiles:
    st.subheader("4. Karakteristik Centroid & Skor 4 Profil Final")
    st.write("Distribusi dan rata-rata skor dimensi dari 332 responden lengkap pada model final Aruna:")

    profile_chars = {
        "Profil": [
            "Tinggi - Seimbang",
            "Tinggi - Sosial Relatif Rendah",
            "Rendah - Seimbang",
            "Rendah - Sosial Relatif Rendah",
        ],
        "Jumlah": [66, 97, 92, 77],
        "Persentase": ["19.88%", "29.22%", "27.71%", "23.19%"],
        "Emotional": [3.495, 3.825, 1.533, 2.463],
        "Social": [3.379, 2.144, 1.367, 0.813],
        "Psychological": [3.538, 3.249, 1.759, 1.755],
    }
    df_profiles = pd.DataFrame(profile_chars)
    st.dataframe(df_profiles, use_container_width=True)

    st.markdown("**Visualisasi Perbandingan Tiga Dimensi Antar Profil:**")
    chart_data = df_profiles.set_index("Profil")[["Emotional", "Social", "Psychological"]]
    st.bar_chart(chart_data)

    st.markdown(
        """
        **Temuan Menarik:**
        * Pada profil **Tinggi - Sosial Relatif Rendah**, responden memiliki skor Emosional tertinggi ($3.825$) dan Psikologis tinggi ($3.249$), namun skor Sosialnya terpaut jauh lebih rendah ($2.144$).
        * Pada profil **Rendah - Sosial Relatif Rendah**, dimensi Sosial mencatat skor terendah di seluruh populasi ($0.813$), mengindikasikan prioritas mendesak pada dukungan dan interaksi sosial.
        """
    )
