
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))


from src.database import (
    initialize_database,
    get_assessment_history,
    get_assessment_by_id
)


# ==================================================
# INITIALIZATION
# ==================================================

initialize_database()

st.title("Riwayat Asesmen")
st.caption(
    "Lihat kembali hasil pemetaan kesejahteraan mental "
    "yang pernah kamu lakukan."
)


# ==================================================
# LOAD HISTORY
# ==================================================

history = get_assessment_history(limit=100)


if not history:
    st.info(
        "Belum ada riwayat asesmen. "
        "Silakan lakukan asesmen MHC-SF terlebih dahulu."
    )

    st.page_link(
        "pages/6_Student_Assessment.py",
        label="Mulai Asesmen",
        icon="📝"
    )

    st.stop()


# ==================================================
# SUMMARY
# ==================================================

latest = history[0]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Asesmen",
        len(history)
    )

with col2:
    st.metric(
        "Asesmen Terakhir",
        pd.to_datetime(latest["created_at"]).strftime(
            "%d %B %Y"
        )
    )


st.divider()


# ==================================================
# HISTORY TABLE
# ==================================================

st.subheader("Daftar Riwayat")

history_table = []

for item in history:
    history_table.append({
        "ID": item["id"],
        "Tanggal": pd.to_datetime(
            item["created_at"]
        ).strftime("%d/%m/%Y %H:%M"),
        "Overall Profile": item["overall_profile"],
        "Relative Pattern": item["pattern_profile"],
        "Emotional": item["emotional"],
        "Social": item["social"],
        "Psychological": item["psychological"]
    })


df_history = pd.DataFrame(history_table)

st.dataframe(
    df_history,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ==================================================
# DETAIL HISTORY
# ==================================================

st.subheader("Detail Hasil Asesmen")

history_options = {
    item["id"]: (
        f'Asesmen #{item["id"]} — '
        f'{pd.to_datetime(item["created_at"]).strftime("%d/%m/%Y %H:%M")}'
    )
    for item in history
}

selected_id = st.selectbox(
    "Pilih asesmen yang ingin dilihat",
    options=list(history_options.keys()),
    format_func=lambda x: history_options[x]
)

selected = get_assessment_by_id(selected_id)


if selected:

    st.markdown("### Profil Kesejahteraan")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Overall Profile",
            selected["overall_profile"]
        )

    with col2:
        st.metric(
            "Relative Pattern",
            selected["pattern_profile"]
        )

    st.markdown("### Skor Dimensi")

    dimensions = {
        "Emotional": selected["emotional"],
        "Social": selected["social"],
        "Psychological": selected["psychological"]
    }

    for dimension, score in dimensions.items():
        st.write(f"**{dimension}** — {score:.2f} / 5")

        st.progress(
            max(0.0, min(float(score) / 5, 1.0))
        )

    st.markdown("### Rekomendasi")

    st.markdown(f"**{selected['recommendation_profile']}**")

    st.write(selected["summary"])

    st.info(f"Fokus pengembangan: {selected['focus']}")

    for index, recommendation in enumerate(
        selected["recommendations"],
        start=1
    ):
        st.write(f"{index}. {recommendation}")

    st.caption(selected["disclaimer"])

    st.caption(
        "Waktu asesmen: " +
        pd.to_datetime(
            selected["created_at"]
        ).strftime("%d %B %Y, %H:%M")
    )
