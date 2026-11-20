
"""
MHC-SF Configuration for Aruna

Primary instrument reference:
Putra, R. F. N. P. (2023).
Adaptasi Mental Health Continuum – Short Form Bahasa Indonesia.
Psychocentrum Review, 5(2), 86–96.
https://doi.org/10.26539/pcr.521768
"""

# =========================================================
# INSTRUMENT INFORMATION
# =========================================================

INSTRUMENT_NAME = "Mental Health Continuum - Short Form"
INSTRUMENT_ABBREVIATION = "MHC-SF"
INSTRUMENT_ITEMS_COUNT = 14

INSTRUCTION = (
    "Jawablah seluruh pertanyaan berikut berdasarkan "
    "apa yang Anda rasakan dan alami selama satu bulan terakhir."
)

QUESTION_STEM = (
    "Seberapa sering Anda merasakan atau mengalami hal-hal berikut?"
)


# =========================================================
# DIMENSION CONFIGURATION
# =========================================================

DIMENSIONS = {
    "Emotional": {
        "label": "Kesejahteraan Emosional",
        "items": [1, 2, 3],
    },
    "Social": {
        "label": "Kesejahteraan Sosial",
        "items": [4, 5, 6, 7, 8],
    },
    "Psychological": {
        "label": "Kesejahteraan Psikologis",
        "items": [9, 10, 11, 12, 13, 14],
    },
}


# =========================================================
# MHC-SF QUESTIONS
# =========================================================

MHC_SF_ITEMS = [
    {
        "id": 1,
        "dimension": "Emotional",
        "question": "Seberapa sering Anda merasa bahagia?",
    },
    {
        "id": 2,
        "dimension": "Emotional",
        "question": (
            "Seberapa sering Anda merasa tertarik "
            "dengan kehidupan?"
        ),
    },
    {
        "id": 3,
        "dimension": "Emotional",
        "question": (
            "Seberapa sering Anda merasa puas "
            "dengan kehidupan yang Anda jalani?"
        ),
    },
    {
        "id": 4,
        "dimension": "Social",
        "question": (
            "Seberapa sering Anda merasa bahwa diri Anda "
            "memberikan kontribusi yang penting bagi masyarakat?"
        ),
    },
    {
        "id": 5,
        "dimension": "Social",
        "question": (
            "Seberapa sering Anda merasa menjadi bagian "
            "dari suatu kelompok atau komunitas, seperti "
            "perkumpulan, lingkungan tempat tinggal, "
            "atau masyarakat sekitar?"
        ),
    },
    {
        "id": 6,
        "dimension": "Social",
        "question": (
            "Seberapa sering Anda merasa bahwa masyarakat "
            "di Indonesia sedang berkembang menjadi tempat "
            "yang lebih baik bagi semua orang?"
        ),
    },
    {
        "id": 7,
        "dimension": "Social",
        "question": (
            "Seberapa sering Anda merasa bahwa "
            "pada dasarnya orang-orang memiliki sifat baik?"
        ),
    },
    {
        "id": 8,
        "dimension": "Social",
        "question": (
            "Seberapa sering Anda merasa bahwa kehidupan "
            "bermasyarakat di Indonesia memiliki keteraturan "
            "dan dapat dipahami?"
        ),
    },
    {
        "id": 9,
        "dimension": "Psychological",
        "question": (
            "Seberapa sering Anda merasa menyukai "
            "sebagian besar sifat yang ada dalam diri Anda?"
        ),
    },
    {
        "id": 10,
        "dimension": "Psychological",
        "question": (
            "Seberapa sering Anda merasa mampu mengelola "
            "berbagai tanggung jawab dalam kehidupan sehari-hari?"
        ),
    },
    {
        "id": 11,
        "dimension": "Psychological",
        "question": (
            "Seberapa sering Anda merasa memiliki hubungan "
            "yang hangat dan saling percaya dengan orang lain?"
        ),
    },
    {
        "id": 12,
        "dimension": "Psychological",
        "question": (
            "Seberapa sering Anda merasa memiliki pengalaman "
            "yang mendorong Anda untuk tumbuh dan menjadi "
            "pribadi yang lebih baik?"
        ),
    },
    {
        "id": 13,
        "dimension": "Psychological",
        "question": (
            "Seberapa sering Anda merasa percaya diri "
            "dalam memikirkan atau mengungkapkan ide "
            "dan pendapat Anda sendiri?"
        ),
    },
    {
        "id": 14,
        "dimension": "Psychological",
        "question": (
            "Seberapa sering Anda merasa bahwa kehidupan "
            "yang Anda jalani memiliki arah atau makna?"
        ),
    },
]


# =========================================================
# RESPONSE OPTIONS
# =========================================================

# Label ditampilkan kepada pengguna dalam Bahasa Indonesia.
# Value tetap menggunakan kategori asli dataset agar
# kompatibel dengan RESPONSE_MAPPING pada preprocessing.py.

RESPONSE_OPTIONS = [
    {
        "label": "Tidak pernah",
        "value": "Never",
        "score": 0,
    },
    {
        "label": "Sekali atau dua kali",
        "value": "Once or twice",
        "score": 1,
    },
    {
        "label": "Sekitar sekali seminggu",
        "value": "About once a week",
        "score": 2,
    },
    {
        "label": "Sekitar 2–3 kali seminggu",
        "value": "About 2-3 times a week",
        "score": 3,
    },
    {
        "label": "Hampir setiap hari",
        "value": "Almost everyday",
        "score": 4,
    },
    {
        "label": "Setiap hari",
        "value": "Everyday",
        "score": 5,
    },
]


# =========================================================
# VALIDATION
# =========================================================

assert len(MHC_SF_ITEMS) == INSTRUMENT_ITEMS_COUNT

assert [
    item["id"] for item in MHC_SF_ITEMS
] == list(range(1, 15))

assert sum(
    len(dimension["items"])
    for dimension in DIMENSIONS.values()
) == INSTRUMENT_ITEMS_COUNT

assert all(
    item["question"].endswith("?")
    for item in MHC_SF_ITEMS
)
