import streamlit as st
import pandas as pd
import numpy as np
from pygrowup import Observation

st.set_page_config(
    page_title="Deteksi Stunting Anak",
    page_icon="👶",
    layout="centered"
)

st.title("👶 Aplikasi Deteksi Stunting")
st.write(
    "Aplikasi untuk menghitung Z-score TB/U dan BB/U "
    "serta menentukan status gizi anak berdasarkan standar antropometri."
)

# Calculator tidak digunakan pada pygrowup2

def safe_zscore(indicator, value, age, sex):
    if pd.isna(value):
        return np.nan

    try:
        obs = Observation(
            sex=sex,
            age_in_months=age
        )

        if indicator == "lhfa":
            z = obs.lhfa(value)
        elif indicator == "wfa":
            z = obs.wfa(value)
        else:
            return np.nan

        return float(z) if z is not None else np.nan

    except Exception:
        return np.nan

def klasifikasi_tbu(z):
    if pd.isna(z):
        return "Data Tidak Lengkap"
    if z < -3:
        return "Sangat Pendek (Severely Stunted)"
    if z < -2:
        return "Pendek (Stunted)"
    if z <= 3:
        return "Normal"
    return "Tinggi"


def klasifikasi_bbu(z):
    if pd.isna(z):
        return "Data Tidak Lengkap"
    if z < -3:
        return "Berat Badan Sangat Kurang"
    if z < -2:
        return "Berat Badan Kurang"
    if z <= 1:
        return "Berat Badan Normal"
    return "Risiko Berat Badan Lebih"


st.subheader("Masukkan Data Anak")

age = st.number_input(
    "Usia Anak (bulan)",
    min_value=0.0,
    max_value=60.0,
    value=24.0,
    step=1.0
)

gender = st.selectbox(
    "Jenis Kelamin",
    ["Male", "Female"]
)

weight = st.number_input(
    "Berat Badan (kg)",
    min_value=0.1,
    max_value=50.0,
    value=10.0,
    step=0.1
)

height = st.number_input(
    "Tinggi/Panjang Badan (cm)",
    min_value=10.0,
    max_value=150.0,
    value=85.0,
    step=0.1
)

posture = st.selectbox(
    "Posisi Pengukuran",
    ["Standing", "Lying"]
)


if st.button("🔍 Deteksi Status Gizi"):

    sex_code = {
    "Male": Observation.MALE,
    "Female": Observation.FEMALE
}[gender]

    is_standing = posture == "Standing"

    z_tbu = safe_zscore(
    "lhfa",
    height,
    age,
    sex_code
)

    z_bbu = safe_zscore(
    "wfa",
    weight,
    age,
    sex_code
)

    status_tbu = klasifikasi_tbu(z_tbu)
    status_bbu = klasifikasi_bbu(z_bbu)

    perlu_verifikasi = (
        pd.notna(z_tbu) and abs(z_tbu) > 5
    )

    if perlu_verifikasi:
        rekomendasi = (
            "Nilai ekstrem - verifikasi ulang pengukuran "
            "sebelum mengambil tindakan"
        )
    elif status_tbu == "Sangat Pendek (Severely Stunted)":
        rekomendasi = (
            "Rujuk segera ke fasilitas kesehatan"
        )
    elif status_tbu == "Pendek (Stunted)":
        rekomendasi = (
            "Pemantauan rutin & edukasi gizi intensif"
        )
    else:
        rekomendasi = (
            "Pemantauan rutin standar (Posyandu)"
        )

    st.subheader("📊 Hasil Deteksi")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Z-score TB/U",
            f"{z_tbu:.2f}" if pd.notna(z_tbu) else "N/A"
        )

    with col2:
        st.metric(
            "Z-score BB/U",
            f"{z_bbu:.2f}" if pd.notna(z_bbu) else "N/A"
        )

    st.write("**Status TB/U:**", status_tbu)
    st.write("**Status BB/U:**", status_bbu)

    st.info(
        f"**Rekomendasi:** {rekomendasi}"
    )

    if perlu_verifikasi:
        st.warning(
            "⚠️ Nilai Z-score TB/U sangat ekstrem. "
            "Pengukuran sebaiknya diverifikasi ulang."
        )
