
import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.mhcsf_config import (
    INSTRUCTION,
    MHC_SF_ITEMS,
    DIMENSIONS,
    RESPONSE_OPTIONS,
)

from src.pipeline import assess_student

from src.database import (
    initialize_database,
    save_assessment
)


# =========================================================
# SESSION STATE RESET
# =========================================================

def reset_assessment():

    for item in MHC_SF_ITEMS:
        widget_key = f"mhcsf_item_{item['id']}"

        st.session_state[widget_key] = None

    st.session_state.pop("assessment_result", None)
    st.session_state.pop("assessment_saved_id", None)

initialize_database()


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.title("Student Assessment")
st.caption("Mental Health Continuum - Short Form (MHC-SF)")

st.write(INSTRUCTION)

st.info(
    "Asesmen ini bertujuan membantu Anda memahami "
    "profil kesejahteraan mental. Hasilnya bukan "
    "diagnosis kondisi kesehatan mental."
)


# =========================================================
# RESPONSE CONFIGURATION
# =========================================================

response_labels = [
    option["label"] for option in RESPONSE_OPTIONS
]

response_mapping = {
    option["label"]: option["value"]
    for option in RESPONSE_OPTIONS
}


# =========================================================
# ASSESSMENT FORM
# =========================================================

with st.form("mhcsf_assessment_form"):

    answers = {}

    for dimension_key, dimension in DIMENSIONS.items():

        st.subheader(dimension["label"])

        dimension_items = [
            item for item in MHC_SF_ITEMS
            if item["dimension"] == dimension_key
        ]

        for item in dimension_items:

            selected = st.radio(
                label=f"{item['id']}. {item['question']}",
                options=response_labels,
                index=None,
                key=f"mhcsf_item_{item['id']}",
                horizontal=False,
            )

            answers[item["id"]] = selected

        st.divider()

    submitted = st.form_submit_button(
        "Kirim Jawaban",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# PROCESS ASSESSMENT
# =========================================================

if submitted:

    unanswered = [
        item_id
        for item_id, answer in answers.items()
        if answer is None
    ]

    if unanswered:

        st.error(
            f"Masih ada {len(unanswered)} pertanyaan "
            "yang belum dijawab. Silakan lengkapi "
            "seluruh pertanyaan."
        )

    else:

        # Convert Indonesian labels to dataset categories
        normalized_answers = [
            response_mapping[answers[item_id]]
            for item_id in range(1, 15)
        ]

        try:

            with st.spinner("Memproses hasil asesmen..."):

                result = assess_student(normalized_answers)

            assessment_id = save_assessment(result)

            st.session_state["assessment_result"] = result
            st.session_state["assessment_saved_id"] = assessment_id

            st.success("Hasil asesmen berhasil disimpan!")

        except Exception as error:

            st.error(
                "Terjadi kesalahan saat memproses asesmen."
            )

            st.exception(error)


# =========================================================
# DISPLAY RESULT
# =========================================================

result = st.session_state.get("assessment_result")

if result:

    st.divider()
    st.header("Hasil Asesmen")

    st.subheader("Profil Kesejahteraan Mental")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Profil Keseluruhan",
            result["overall_profile"],
        )

    with col2:
        st.metric(
            "Pola Dimensi",
            result["pattern_profile"],
        )

    st.subheader("Skor Dimensi")

    dimension_scores = result["dimension_scores"]

    for dimension_key, dimension in DIMENSIONS.items():

        score = dimension_scores[dimension_key]

        st.write(
            f"**{dimension['label']}**"
        )

        st.progress(
            max(0.0, min(float(score) / 5.0, 1.0))
        )

        st.caption(f"Skor: {score:.2f} / 5.00")

    st.divider()

    recommendation = result["recommendation"]

    st.subheader(recommendation["profile_name"])

    st.write(recommendation["summary"])

    st.markdown("**Fokus pengembangan**")
    st.write(recommendation["focus"])

    st.markdown("**Rekomendasi**")

    for index, suggestion in enumerate(
        recommendation["recommendations"],
        start=1,
    ):
        st.write(f"{index}. {suggestion}")

    st.warning(recommendation["disclaimer"])

    st.button(
        "Hapus Hasil Asesmen",
        on_click=reset_assessment,
    )
