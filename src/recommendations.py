
def generate_recommendations(prediction):
    """
    Menghasilkan rekomendasi berdasarkan profil hasil clustering Aruna.

    Parameters
    ----------
    prediction : dict
        Hasil dari fungsi predict_profile().

    Returns
    -------
    dict
        Ringkasan profil dan rekomendasi tindak lanjut.
    """

    overall = prediction["overall_profile"]
    pattern = prediction["pattern_profile"]

    profile_rules = {
        ("Tinggi", "Seimbang"): {
            "profile_name": "Kesejahteraan Tinggi dan Seimbang",
            "summary": (
                "Hasil pemetaan menunjukkan bahwa kesejahteraan "
                "secara keseluruhan tergolong tinggi dengan pola "
                "dimensi yang relatif seimbang."
            ),
            "focus": "Mempertahankan kesejahteraan",
            "recommendations": [
                "Pertahankan aktivitas yang selama ini mendukung kesejahteraan.",
                "Jaga keseimbangan antara kegiatan akademik, sosial, dan pribadi.",
                "Luangkan waktu untuk refleksi dan evaluasi kondisi diri."
            ]
        },

        ("Tinggi", "Sosial Relatif Rendah"): {
            "profile_name": "Kesejahteraan Tinggi dengan Aspek Sosial Relatif Rendah",
            "summary": (
                "Kesejahteraan secara keseluruhan tergolong tinggi, "
                "tetapi dimensi sosial relatif lebih rendah dibandingkan "
                "dimensi lainnya."
            ),
            "focus": "Memperkuat keterhubungan sosial",
            "recommendations": [
                "Luangkan waktu untuk berinteraksi dengan teman atau orang terdekat.",
                "Coba terlibat dalam kegiatan komunitas atau aktivitas bersama.",
                "Bangun komunikasi secara bertahap dengan orang yang dipercaya."
            ]
        },

        ("Rendah", "Seimbang"): {
            "profile_name": "Kesejahteraan Rendah dan Seimbang",
            "summary": (
                "Hasil pemetaan menunjukkan bahwa tingkat kesejahteraan "
                "secara keseluruhan relatif rendah, tanpa satu dimensi "
                "yang tampak jauh lebih rendah secara relatif."
            ),
            "focus": "Membangun kesejahteraan secara menyeluruh",
            "recommendations": [
                "Mulai dengan aktivitas sederhana yang membantu menjaga rutinitas harian.",
                "Kenali aktivitas yang membuat diri merasa lebih nyaman dan bermakna.",
                "Pertimbangkan untuk berbagi cerita dengan orang yang dipercaya.",
                "Jika kondisi mengganggu aktivitas sehari-hari, pertimbangkan mencari dukungan profesional."
            ]
        },

        ("Rendah", "Sosial Relatif Rendah"): {
            "profile_name": "Kesejahteraan Rendah dengan Aspek Sosial Relatif Rendah",
            "summary": (
                "Kesejahteraan secara keseluruhan relatif rendah, "
                "dan dimensi sosial juga relatif lebih rendah "
                "dibandingkan dimensi lainnya."
            ),
            "focus": "Membangun kesejahteraan dan keterhubungan sosial",
            "recommendations": [
                "Mulai menjalin interaksi ringan dengan teman atau orang yang dipercaya.",
                "Coba mengikuti aktivitas bersama dalam lingkungan yang terasa nyaman.",
                "Bangun rutinitas sederhana untuk menjaga kebutuhan diri.",
                "Pertimbangkan menghubungi layanan konseling atau dukungan profesional jika membutuhkan bantuan lebih lanjut."
            ]
        }
    }

    key = (overall, pattern)

    if key not in profile_rules:
        raise ValueError(
            f"Kombinasi profil tidak dikenali: {key}"
        )

    result = profile_rules[key].copy()

    result["overall_profile"] = overall
    result["pattern_profile"] = pattern
    result["scores"] = prediction.get("scores", {})

    result["disclaimer"] = (
        "Hasil ini merupakan pemetaan kesejahteraan berdasarkan "
        "jawaban kuesioner, bukan diagnosis klinis. Rekomendasi "
        "bersifat umum dan tidak menggantikan konsultasi profesional."
    )

    return result
