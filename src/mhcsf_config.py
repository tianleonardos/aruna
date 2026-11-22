"""Konfigurasi Instrumen MHC-SF untuk Proyek ARUNA.

Referensi instrumen utama:
Putra, R. F. N. P. (2023).
Adaptasi Mental Health Continuum - Short Form Bahasa Indonesia.
Psychocentrum Review, 5(2), 86–96.
https://doi.org/10.26539/pcr.521768

Dilengkapi keterangan tambahan (helper_text) untuk mode flashcard edukatif.
"""

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

# Konfigurasi 3 dimensi psikososial
DIMENSIONS = {
    "Emotional": {
        "label": "Kesejahteraan Emosional",
        "desc": "Mengukur kebahagiaan, ketertarikan pada hidup, dan kepuasan hidup.",
        "color": "#F472B6", # Rose / Pink
        "items": [1, 2, 3],
    },
    "Social": {
        "label": "Kesejahteraan Sosial",
        "desc": "Mengukur kontribusi, keterhubungan komunitas, dan kepercayaan sosial.",
        "color": "#38BDF8", # Sky Blue
        "items": [4, 5, 6, 7, 8],
    },
    "Psychological": {
        "label": "Kesejahteraan Psikologis",
        "desc": "Mengukur penerimaan diri, kemandirian, dan tujuan hidup.",
        "color": "#34D399", # Emerald Green
        "items": [9, 10, 11, 12, 13, 14],
    },
}

# 14 Butir Pertanyaan MHC-SF beserta panduan pemahaman (helper_text)
MHC_SF_ITEMS = [
    {
        "id": 1,
        "dimension": "Emotional",
        "question": "Seberapa sering Anda merasa bahagia?",
        "helper_text": "Meninjau frekuensi rasa gembira, ceria, dan suasana hati positif yang Anda rasakan selama sebulan terakhir dalam menjalani rutinitas harian.",
    },
    {
        "id": 2,
        "dimension": "Emotional",
        "question": "Seberapa sering Anda merasa tertarik dengan kehidupan?",
        "helper_text": "Mengukur rasa antusias, rasa ingin tahu, serta semangat untuk mempelajari hal baru atau menjalani hari-hari Anda.",
    },
    {
        "id": 3,
        "dimension": "Emotional",
        "question": "Seberapa sering Anda merasa puas dengan kehidupan yang Anda jalani?",
        "helper_text": "Menilai sejauh mana Anda merasa bersyukur, nyaman, dan menerima perjalanan hidup yang sedang Anda jalani saat ini.",
    },
    {
        "id": 4,
        "dimension": "Social",
        "question": "Seberapa sering Anda merasa bahwa diri Anda memberikan kontribusi yang penting bagi masyarakat?",
        "helper_text": "Mengukur perasaan bahwa ide, tenaga, atau karya Anda memiliki arti dan memberi manfaat bagi orang lain di sekitar Anda.",
    },
    {
        "id": 5,
        "dimension": "Social",
        "question": "Seberapa sering Anda merasa menjadi bagian dari suatu kelompok atau komunitas?",
        "helper_text": "Meninjau rasa keterhubungan (sense of belonging) dan kehangatan saat Anda berada di lingkungan pertemanan, organisasi, atau kampus.",
    },
    {
        "id": 6,
        "dimension": "Social",
        "question": "Seberapa sering Anda merasa bahwa masyarakat berkembang menjadi tempat yang lebih baik bagi semua orang?",
        "helper_text": "Mengukur rasa optimisme dan harapan positif Anda terhadap perkembangan lingkungan sosial di sekitar Anda.",
    },
    {
        "id": 7,
        "dimension": "Social",
        "question": "Seberapa sering Anda merasa bahwa pada dasarnya orang-orang memiliki sifat baik?",
        "helper_text": "Menilai tingkat kepercayaan dan keyakinan Anda bahwa kebanyakan orang memiliki niat baik dan ketulusan dalam berinteraksi.",
    },
    {
        "id": 8,
        "dimension": "Social",
        "question": "Seberapa sering Anda merasa bahwa kehidupan bermasyarakat memiliki keteraturan dan dapat dipahami?",
        "helper_text": "Meninjau apakah dinamika sosial, aturan, dan tatanan di lingkungan sekitar Anda terasa masuk akal dan dapat dimengerti.",
    },
    {
        "id": 9,
        "dimension": "Psychological",
        "question": "Seberapa sering Anda merasa menyukai sebagian besar sifat yang ada dalam diri Anda?",
        "helper_text": "Mengukur penerimaan diri (self-acceptance), baik terhadap kelebihan maupun keterbatasan pribadi tanpa rasa minder.",
    },
    {
        "id": 10,
        "dimension": "Psychological",
        "question": "Seberapa sering Anda merasa mampu mengelola berbagai tanggung jawab dalam kehidupan sehari-hari?",
        "helper_text": "Menilai kemampuan Anda dalam membagi waktu, menyelesaikan tugas kuliah, dan menghadapi tuntutan aktivitas sehari-hari.",
    },
    {
        "id": 11,
        "dimension": "Psychological",
        "question": "Seberapa sering Anda merasa memiliki hubungan yang hangat dan saling percaya dengan orang lain?",
        "helper_text": "Meninjau apakah Anda memiliki sahabat, pasangan, atau keluarga yang selalu mendukung dan tempat Anda bisa bercerita secara jujur.",
    },
    {
        "id": 12,
        "dimension": "Psychological",
        "question": "Seberapa sering Anda merasa memiliki pengalaman yang mendorong Anda untuk tumbuh dan menjadi pribadi yang lebih baik?",
        "helper_text": "Mengukur kemauan untuk belajar dari kesalahan, mengembangkan potensi diri, dan memperluas wawasan kepribadian.",
    },
    {
        "id": 13,
        "dimension": "Psychological",
        "question": "Seberapa sering Anda merasa percaya diri dalam memikirkan atau mengungkapkan ide dan pendapat Anda sendiri?",
        "helper_text": "Menilai kemandirian (autonomy) dan keteguhan Anda dalam memegang prinsip tanpa mudah tertekan oleh opini orang lain.",
    },
    {
        "id": 14,
        "dimension": "Psychological",
        "question": "Seberapa sering Anda merasa bahwa kehidupan yang Anda jalani memiliki arah atau makna?",
        "helper_text": "Menilai kejelasan tujuan hidup, cita-cita, serta arti mendalam dari setiap langkah yang sedang Anda perjuangkan.",
    },
]

# 6 Pilihan Frekuensi Jawaban Ordinal (0 - 5)
RESPONSE_OPTIONS = [
    {"label": "Tidak pernah", "value": "Never", "score": 0},
    {"label": "Sekali atau dua kali", "value": "Once or twice", "score": 1},
    {"label": "Sekitar sekali seminggu", "value": "About once a week", "score": 2},
    {"label": "Sekitar 2–3 kali seminggu", "value": "About 2-3 times a week", "score": 3},
    {"label": "Hampir setiap hari", "value": "Almost everyday", "score": 4},
    {"label": "Setiap hari", "value": "Everyday", "score": 5},
]
