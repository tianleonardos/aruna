"""Sistem Desain, Tema Visual Modern & Vektor Kesehatan Mental ARUNA.

Fitur:
1. Identitas visual Aruna berbasis logo resmi (palet ungu #5A069A dan aksen gradien sunset).
2. Tipografi 'Alan Sans Semibold' warna #5A069A untuk penulisan Aruna.
3. Sinkronisasi responsif Dark Mode & Light Mode dengan Streamlit native theme.
4. Opsi penyembunyian sidebar otomatis untuk mahasiswa/tamu (hanya admin yang memiliki sidebar).
5. Animasi loading 3 Dimensi unik bertema mental health (Emosional, Sosial, Psikologis).
"""

from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
LOGO_SVG_PATH = ROOT_DIR / "assets" / "icon_logo.svg"
LOGO_PNG_PATH = ROOT_DIR / "assets" / "icon_logo.png"

# ===========================================================================
# 1. ILUSTRASI VEKTOR ORGANIK TANPA OUTLINE
# ===========================================================================

VECTORS = {
    # 1. Mind & Growth: Siluet pikiran organik dengan daun yang mekar lembut
    "flourishing_mind": """
    <svg viewBox="0 0 200 200" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8637F4" stop-opacity="0.22" />
                <stop offset="100%" stop-color="#5A069A" stop-opacity="0.10" />
            </linearGradient>
            <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8637F4" />
                <stop offset="100%" stop-color="#5A069A" />
            </linearGradient>
            <linearGradient id="sunGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FE9B53" />
                <stop offset="100%" stop-color="#FF5B81" />
            </linearGradient>
            <linearGradient id="softPink" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FECF92" />
                <stop offset="100%" stop-color="#FE9B53" />
            </linearGradient>
        </defs>
        <circle cx="100" cy="100" r="90" fill="url(#bgGrad)" />
        <circle cx="145" cy="65" r="30" fill="url(#sunGrad)" opacity="0.9" />
        <path d="M65,155 C55,130 50,105 60,80 C70,55 95,45 120,52 C145,59 155,85 145,115 C140,130 130,145 115,155 Z" fill="#D6ABF0" opacity="0.65" />
        <path d="M100,75 C90,45 110,30 125,40 C140,50 120,70 100,75 Z" fill="url(#leafGrad)" />
        <path d="M85,90 C65,70 75,50 95,58 C115,66 100,85 85,90 Z" fill="url(#leafGrad)" opacity="0.85" />
        <ellipse cx="78" cy="120" rx="14" ry="9" fill="url(#softPink)" opacity="0.75" transform="rotate(-15, 78, 120)" />
        <circle cx="135" cy="125" r="7" fill="#FECF92" opacity="0.9" />
    </svg>
    """,

    # 2. Balance: Keseimbangan 3 dimensi seperti batu zen bertingkat harmonis
    "balance_harmony": """
    <svg viewBox="0 0 200 200" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="stoneBottom" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#5A069A" />
                <stop offset="100%" stop-color="#49047D" />
            </linearGradient>
            <linearGradient id="stoneMid" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8637F4" />
                <stop offset="100%" stop-color="#662E91" />
            </linearGradient>
            <linearGradient id="stoneTop" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FE9B53" />
                <stop offset="100%" stop-color="#FF5B81" />
            </linearGradient>
        </defs>
        <ellipse cx="100" cy="165" rx="75" ry="14" fill="#5A069A" opacity="0.12" />
        <path d="M45,150 C45,130 70,125 100,125 C130,125 155,130 155,150 C155,168 130,172 100,172 C70,172 45,168 45,150 Z" fill="url(#stoneBottom)" opacity="0.9" />
        <path d="M60,105 C60,90 80,85 102,85 C124,85 142,90 142,105 C142,120 124,124 102,124 C80,124 60,120 60,105 Z" fill="url(#stoneMid)" opacity="0.9" />
        <path d="M78,65 C78,52 90,48 104,48 C118,48 128,52 128,65 C128,78 118,82 104,82 C90,82 78,78 78,65 Z" fill="url(#stoneTop)" opacity="0.9" />
        <path d="M104,48 C100,32 112,24 116,28 C120,32 110,44 104,48 Z" fill="#FECF92" />
    </svg>
    """,

    # 3. Student Journey: Buku terbuka organik bertunas daun mekar
    "student_journey": """
    <svg viewBox="0 0 200 200" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="pageLeft" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8637F4" stop-opacity="0.3" />
                <stop offset="100%" stop-color="#5A069A" stop-opacity="0.8" />
            </linearGradient>
            <linearGradient id="pageRight" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FE9B53" stop-opacity="0.3" />
                <stop offset="100%" stop-color="#FF5B81" stop-opacity="0.8" />
            </linearGradient>
            <linearGradient id="sunBloom" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FECF92" />
                <stop offset="100%" stop-color="#FE9B53" />
            </linearGradient>
        </defs>
        <circle cx="100" cy="100" r="85" fill="#5A069A" opacity="0.10" />
        <circle cx="100" cy="55" r="26" fill="url(#sunBloom)" opacity="0.85" />
        <path d="M35,135 C55,120 80,122 100,132 C100,158 75,160 35,160 Z" fill="url(#pageLeft)" />
        <path d="M165,135 C145,120 120,122 100,132 C100,158 125,160 165,160 Z" fill="url(#pageRight)" />
        <path d="M100,130 C90,100 100,80 100,80 C100,80 110,100 100,130 Z" fill="#5A069A" />
        <path d="M100,95 C115,85 125,92 120,105 C112,110 104,102 100,95 Z" fill="#8637F4" />
        <path d="M100,105 C85,95 75,102 80,115 C88,120 96,112 100,105 Z" fill="#D6ABF0" />
    </svg>
    """,

    # 4. Research Matrix: Klaster multidimensi bergradien ungu halus
    "research_matrix": """
    <svg viewBox="0 0 200 200" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="gridGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8637F4" stop-opacity="0.2" />
                <stop offset="100%" stop-color="#5A069A" stop-opacity="0.05" />
            </linearGradient>
        </defs>
        <rect x="20" y="20" width="160" height="160" rx="30" fill="url(#gridGrad)" />
        <circle cx="135" cy="65" r="22" fill="#5A069A" opacity="0.85" />
        <circle cx="135" cy="65" r="9" fill="#F5EEFD" />
        <circle cx="65" cy="75" r="19" fill="#8637F4" opacity="0.85" />
        <circle cx="65" cy="75" r="7" fill="#FAF5FF" />
        <circle cx="70" cy="135" r="21" fill="#FE9B53" opacity="0.85" />
        <circle cx="70" cy="135" r="8" fill="#FFF7ED" />
        <circle cx="130" cy="135" r="18" fill="#FF5B81" opacity="0.85" />
        <circle cx="130" cy="135" r="7" fill="#FFF1F2" />
        <path d="M65,75 Q100,100 135,65" stroke="#7751B0" stroke-width="3" stroke-dasharray="5,5" fill="none" opacity="0.7" />
        <path d="M70,135 Q100,100 130,135" stroke="#7751B0" stroke-width="3" stroke-dasharray="5,5" fill="none" opacity="0.7" />
        <path d="M65,75 Q70,105 70,135" stroke="#7751B0" stroke-width="3" stroke-dasharray="5,5" fill="none" opacity="0.7" />
        <path d="M135,65 Q130,100 130,135" stroke="#7751B0" stroke-width="3" stroke-dasharray="5,5" fill="none" opacity="0.7" />
    </svg>
    """
}


# ===========================================================================
# 2. LOGO ASSETS & BRANDING HELPERS
# ===========================================================================

@st.cache_data
def get_logo_svg() -> str:
    """Membaca isi file SVG logo resmi di folder assets."""
    if LOGO_SVG_PATH.exists():
        try:
            return LOGO_SVG_PATH.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""


@st.cache_data
def get_logo_base64() -> str:
    """Mengonversi file SVG/PNG logo resmi ke format Data URL Base64 untuk tag <img>."""
    # Utamakan SVG untuk rendering vektor tajam dan ukuran ringan (~19KB)
    if LOGO_SVG_PATH.exists():
        try:
            data = LOGO_SVG_PATH.read_bytes()
            b64 = base64.b64encode(data).decode("utf-8")
            return f"data:image/svg+xml;base64,{b64}"
        except Exception:
            pass
    # Fallback ke PNG jika SVG tidak terbaca
    if LOGO_PNG_PATH.exists():
        try:
            data = LOGO_PNG_PATH.read_bytes()
            b64 = base64.b64encode(data).decode("utf-8")
            return f"data:image/png;base64,{b64}"
        except Exception:
            pass
    return ""


def get_logo_file_path() -> str:
    """Mengembalikan path file logo fisik untuk widget Streamlit (page_icon / st.logo)."""
    if LOGO_PNG_PATH.exists():
        return str(LOGO_PNG_PATH)
    if LOGO_SVG_PATH.exists():
        return str(LOGO_SVG_PATH)
    return "🌱"


def render_brand_header(subtitle: str = "", badge: str = "PBL Machine Learning · TEK1302") -> None:
    """Merender banner header resmi Aruna dengan Logo dan font Alan Sans Semibold warna #5A069A."""
    logo_src = get_logo_base64()
    badge_html = f'<div class="aruna-badge">{badge}</div>' if badge else ""
    subtitle_html = f'<div style="font-size: 1.05rem; color: var(--text-color); opacity: 0.85; margin-top: 4px;">{subtitle}</div>' if subtitle else ""

    header_html = f"""
    <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 20px; padding: 6px 0;">
        <img src="{logo_src}" alt="Aruna Logo" style="width: 58px; height: 58px; object-fit: contain;" />
        <div>
            {badge_html}
            <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.3rem; line-height: 1.1;">Aruna</h1>
            {subtitle_html}
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


# ===========================================================================
# 3. CSS RESPONSIF STREAMLIT NATIVE DARK & LIGHT MODE (BRAND #5A069A)
# ===========================================================================

def generate_css(hide_sidebar: bool = False) -> str:
    sidebar_css = """
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    """ if hide_sidebar else ""

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Alan+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    {sidebar_css}

    /* Font Family & Layout Global */
    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* Tipografi Khusus Logo & Brand ARUNA: Font Alan Sans Semibold warna #5A069A */
    .aruna-brand-title {{
        font-family: 'Alan Sans', 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        color: #5A069A !important;
        letter-spacing: -0.015em !important;
    }}

    /* Gunakan variabel Streamlit resmi agar sinkron sempurna dengan toggle tema */
    .stApp, [data-testid="stAppViewContainer"], section.main, .block-container {{
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }}

    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    /* Kartu Modern Beradaptasi Sempurna dengan Light & Dark Mode */
    .aruna-card {{
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(90, 6, 154, 0.16) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        color: var(--text-color) !important;
        box-shadow: 0 8px 24px rgba(90, 6, 154, 0.04) !important;
        margin-bottom: 20px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .aruna-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(90, 6, 154, 0.08) !important;
        border-color: rgba(90, 6, 154, 0.3) !important;
    }}

    .aruna-card h1, .aruna-card h2, .aruna-card h3, .aruna-card h4, .aruna-card p, .aruna-card span, .aruna-card div {{
        color: var(--text-color) !important;
    }}

    /* Flashcard Soal Per Soal */
    .aruna-flashcard {{
        background-color: var(--secondary-background-color) !important;
        border: 2px solid rgba(90, 6, 154, 0.22) !important;
        border-radius: 24px !important;
        padding: 32px 28px !important;
        color: var(--text-color) !important;
        margin: 18px 0 !important;
        box-shadow: 0 8px 25px rgba(90, 6, 154, 0.05) !important;
    }}

    .aruna-helper-box {{
        background-color: rgba(90, 6, 154, 0.08) !important;
        border-left: 4px solid #5A069A !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin: 16px 0 !important;
        color: var(--text-color) !important;
        font-size: 0.94rem !important;
        line-height: 1.6 !important;
    }}

    /* Badge & Tag - Nuansa Brand Ungu #5A069A & Sunset Aksen */
    .aruna-badge {{
        display: inline-block !important;
        padding: 6px 14px !important;
        border-radius: 999px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        background-color: rgba(90, 6, 154, 0.12) !important;
        color: #5A069A !important;
        margin-bottom: 10px !important;
    }}

    .aruna-badge-sunset {{
        display: inline-block !important;
        padding: 6px 14px !important;
        border-radius: 999px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        background-color: rgba(254, 155, 83, 0.18) !important;
        color: #EA580C !important;
        margin-bottom: 10px !important;
    }}

    /* Tombol Modern Berwarna Brand Ungu */
    .stButton>button {{
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        transition: all 0.2s ease !important;
    }}

    .stButton>button[kind="primary"], .stButton>button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(135deg, #5A069A 0%, #7E22CE 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(90, 6, 154, 0.28) !important;
    }}

    .stButton>button[kind="primary"]:hover, .stButton>button[data-testid="stBaseButton-primary"]:hover {{
        background: linear-gradient(135deg, #49047D 0%, #6B21A8 100%) !important;
        box-shadow: 0 6px 20px rgba(90, 6, 154, 0.40) !important;
        transform: translateY(-1px);
    }}

    /* Metrik Card */
    div[data-testid="stMetric"] {{
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(90, 6, 154, 0.18) !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        color: var(--text-color) !important;
    }}

    div[data-testid="stMetricLabel"] {{
        color: var(--text-color) !important;
        opacity: 0.85 !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: #5A069A !important;
        font-weight: 700 !important;
    }}

    /* ANIMASI 3D LOADING MENTAL HEALTH */
    @keyframes aruna-orbit {{
        0% {{ transform: rotate(0deg) scale(0.95); }}
        50% {{ transform: rotate(180deg) scale(1.06); }}
        100% {{ transform: rotate(360deg) scale(0.95); }}
    }}

    @keyframes aruna-pulse-core {{
        0%, 100% {{ transform: scale(0.9); opacity: 0.7; }}
        50% {{ transform: scale(1.1); opacity: 1; }}
    }}

    .aruna-loader-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        text-align: center;
    }}

    .aruna-loader-spinner {{
        position: relative;
        width: 120px;
        height: 120px;
        margin-bottom: 24px;
        animation: aruna-orbit 3.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    }}

    .aruna-dot {{
        position: absolute;
        width: 32px;
        height: 32px;
        border-radius: 50%;
    }}

    /* Emosional: Sunset Rose dari palet logo */
    .dot-emotional {{
        top: 0;
        left: 44px;
        background: radial-gradient(circle, #FF5B81 0%, #E11D48 100%);
        box-shadow: 0 0 20px rgba(255, 91, 129, 0.7);
    }}

    /* Sosial: Golden Coral dari palet logo */
    .dot-social {{
        bottom: 12px;
        left: 10px;
        background: radial-gradient(circle, #FE9B53 0%, #EA580C 100%);
        box-shadow: 0 0 20px rgba(254, 155, 83, 0.7);
    }}

    /* Psikologis: Deep Purple dari palet logo */
    .dot-psychological {{
        bottom: 12px;
        right: 10px;
        background: radial-gradient(circle, #8637F4 0%, #5A069A 100%);
        box-shadow: 0 0 20px rgba(90, 6, 154, 0.7);
    }}

    /* Inti: Sunset Peach glow */
    .aruna-center-glow {{
        position: absolute;
        top: 42px;
        left: 42px;
        width: 36px;
        height: 36px;
        background: radial-gradient(circle, #FECF92 0%, rgba(254, 207, 146, 0) 70%);
        border-radius: 50%;
        animation: aruna-pulse-core 2s ease-in-out infinite;
    }}
    </style>
    """


def apply_theme(hide_sidebar: bool = False) -> None:
    """Mengaplikasikan CSS responsif Dark/Light mode ke antarmuka Streamlit."""
    st.markdown(generate_css(hide_sidebar=hide_sidebar), unsafe_allow_html=True)


def get_vector(name: str) -> str:
    """Mengambil kode SVG vektor organik berdasarkan nama identifier."""
    return VECTORS.get(name, "")


def render_mental_health_loader(message: str = "Sedang menyelaraskan dimensi emosional, sosial, dan psikologis...") -> str:
    """Menghasilkan HTML animasi 3D loading bertema mental health."""
    return f"""
    <div class="aruna-loader-container">
        <div class="aruna-loader-spinner">
            <div class="aruna-center-glow"></div>
            <div class="aruna-dot dot-emotional" title="Emotional Dimension"></div>
            <div class="aruna-dot dot-social" title="Social Dimension"></div>
            <div class="aruna-dot dot-psychological" title="Psychological Dimension"></div>
        </div>
        <div style="font-weight: 600; font-size: 1.15rem; color: #5A069A; margin-bottom: 6px;">
            {message}
        </div>
        <div style="font-size: 0.88rem; color: var(--text-color); opacity: 0.75;">
            Menganalisis pola multidimensional MHC-SF secara objektif...
        </div>
    </div>
    """
