
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Aruna | Mental Well-Being",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero-container {
        padding: 2.5rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #E8F3EF, #F3F7F5);
        margin-bottom: 2rem;
    }

    .hero-title {
        color: #245B4A;
        font-size: 2.8rem;
        font-weight: 750;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        color: #526B61;
        font-size: 1.1rem;
        line-height: 1.7;
    }

    .section-title {
        color: #245B4A;
        font-size: 1.4rem;
        font-weight: 650;
        margin-top: 1.5rem;
    }

    .feature-card {
        background-color: #FFFFFF;
        border: 1px solid #E4EBE7;
        border-radius: 14px;
        padding: 1.3rem;
        min-height: 175px;
    }

    .feature-title {
        color: #245B4A;
        font-size: 1.1rem;
        font-weight: 650;
        margin-bottom: 0.5rem;
    }

    .feature-description {
        color: #64756D;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .footer {
        color: #89968F;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 4rem;
        padding-top: 1rem;
        border-top: 1px solid #E8EEEA;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("## 🌱 ARUNA")
    st.caption("Mental Well-Being Profiling")
    st.divider()

    st.markdown(
        """
        **Selamat datang di Aruna.**

        Platform pemetaan profil kesejahteraan
        mental berdasarkan dimensi psikososial.
        """
    )

    st.divider()
    st.caption("ARUNA MACHINE LEARNING")
    st.caption("Version 1.0")

# ==========================================
# HERO SECTION
# ==========================================

st.markdown("""
<div class="hero-container">
    <div class="hero-title">Welcome to Aruna.</div>
    <div class="hero-subtitle">
        Kenali profil kesejahteraan mentalmu melalui
        pemetaan dimensi emosional, sosial, dan psikologis.
        <br><br>
        Memahami diri adalah langkah awal untuk
        membangun kesejahteraan yang lebih baik.
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# INTRODUCTION
# ==========================================

st.markdown(
    '<div class="section-title">Mengenal Aruna</div>',
    unsafe_allow_html=True
)

st.write(
    """
    Aruna merupakan aplikasi pemetaan profil kesejahteraan
    mental mahasiswa menggunakan pendekatan **Unsupervised
    Machine Learning**.

    Dengan menggunakan instrumen Mental Health Continuum –
    Short Form (MHC-SF), Aruna memetakan kesejahteraan mental
    melalui tiga dimensi utama, yaitu emosional, sosial,
    dan psikologis.

    Hasil pemetaan digunakan untuk memberikan gambaran
    profil kesejahteraan serta rekomendasi pengembangan diri
    yang relevan.
    """
)

# ==========================================
# FEATURE SECTION
# ==========================================

st.markdown(
    '<div class="section-title">Fitur Utama</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🧠 Student Assessment</div>
        <div class="feature-description">
            Isi asesmen MHC-SF untuk memperoleh gambaran
            profil kesejahteraan mental berdasarkan
            tiga dimensi psikososial.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Profile Mapping</div>
        <div class="feature-description">
            Kenali hasil pemetaan profil kesejahteraan
            melalui pendekatan clustering dan
            analisis pola relatif antardimensi.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🌱 Personal Recommendation</div>
        <div class="feature-description">
            Dapatkan rekomendasi refleksi dan
            pengembangan diri berdasarkan
            hasil pemetaan profil.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# DISCLAIMER
# ==========================================

st.info(
    """
    **Catatan:** Aruna merupakan sarana pemetaan dan
    refleksi kesejahteraan mental, bukan alat diagnosis
    atau pengganti konsultasi profesional.
    """
)

# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    ARUNA — Mental Well-Being Profiling Application<br>
    Powered by Unsupervised Machine Learning
</div>
""", unsafe_allow_html=True)
