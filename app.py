
import streamlit as st

st.set_page_config(
    page_title="Aruna",
    page_icon="🌱",
    layout="wide"
)

pages = {
    "Mahasiswa": [
        st.Page(
            "pages/6_Student_Assessment.py",
            title="Student Assessment",
            icon="📝",
            default=True
        ),
        st.Page(
            "pages/7_Student_History.py",
            title="Student History",
            icon="📊"
        ),
    ],
    "Administrator": [
        st.Page(
            "pages/1_Admin_Dashboard.py",
            title="Admin Dashboard",
            icon="🏠"
        ),
        st.Page(
            "pages/2_Dataset_Management.py",
            title="Dataset Management",
            icon="📁"
        ),
        st.Page(
            "pages/3_Model_Training.py",
            title="Model Training",
            icon="⚙️"
        ),
        st.Page(
            "pages/4_Model_Evaluation.py",
            title="Model Evaluation",
            icon="📈"
        ),
        st.Page(
            "pages/5_Model_Registry.py",
            title="Model Registry",
            icon="🗃️"
        ),
    ],
}

navigation = st.navigation(pages)
navigation.run()
