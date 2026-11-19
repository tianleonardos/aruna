
from src.prediction import predict_from_answers
from src.recommendations import generate_recommendations


def assess_student(answers):
    """
    Menjalankan keseluruhan pipeline assessment Aruna.

    Tahapan:
    1. Menerima 14 jawaban MHC-SF.
    2. Melakukan encoding dan dimension scoring.
    3. Memprediksi profil menggunakan clustering.
    4. Menghasilkan rekomendasi berdasarkan profil.

    Parameters
    ----------
    answers : list, tuple, atau dict
        Jawaban 14 item MHC-SF.

    Returns
    -------
    dict
        Hasil assessment lengkap Aruna.
    """

    # 1. Prediksi profil
    prediction = predict_from_answers(answers)

    # 2. Generate rekomendasi
    recommendation = generate_recommendations(prediction)

    # 3. Gabungkan hasil
    result = {
        "item_scores": prediction["item_scores"],
        "dimension_scores": prediction["dimension_scores"],
        "overall_profile": prediction["overall_profile"],
        "pattern_profile": prediction["pattern_profile"],
        "recommendation": recommendation
    }

    return result
