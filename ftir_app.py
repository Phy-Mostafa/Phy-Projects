import streamlit as st
import numpy as np
import matplotlib as plt
import re

# ========== Title ==========
st.title("FTIR Spectrum Plotter from Gaussian Output")
st.markdown("Upload a Gaussian output file (.log or .out) and view the FTIR spectrum.")

# ========== File Upload ==========
uploaded_file = st.file_uploader("Choose a Gaussian output file", type=["log", "out"])

# ========== Functions ==========

def extract_frequencies_intensities(content):
    """
    Extract frequencies and IR intensities from Gaussian output text.
    Returns two numpy arrays: frequencies (cm-1) and intensities (arbitrary units).
    """
    freqs = []
    intensities = []

    # regex to match lines with frequencies and intensities
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "Frequencies --" in line:
            freq_vals = [float(x) for x in line.split()[2:]]
            inten_line = lines[i + 2]  # IR Inten line is 2 lines after
            inten_vals = [float(x) for x in inten_line.split()[3:]]
            freqs.extend(freq_vals)
            intensities.extend(inten_vals)

    return np.array(freqs), np.array(intensities)

def gaussian_broadening(freqs, intensities, fwhm=10, resolution=1):
    """
    Apply Gaussian broadening to the stick spectrum.
    """
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    x = np.arange(min(freqs) - 100, max(freqs) + 100, resolution)
    y = np.zeros_like(x)

    for f, inten in zip(freqs, intensities):
        y += inten * np.exp(-((x - f) ** 2) / (2 * sigma ** 2))

    return x, y

# ========== Main Logic ==========

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    freqs, intensities = extract_frequencies_intensities(content)

    if len(freqs) == 0:
        st.error("No vibrational frequencies found in the file.")
    else:
        st.success(f"Extracted {len(freqs)} vibrational modes.")

        # === User controls ===
        fwhm = st.slider("Gaussian broadening (FWHM, cm⁻¹)", 1, 50, 10)
        xlim = st.slider("Frequency range (cm⁻¹)", 0, int(max(freqs) + 500), (0, int(max(freqs) + 100)))

        x, y = gaussian_broadening(freqs, intensities, fwhm=fwhm)

        # === Plot ===
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(x, y, color='blue', lw=2)
        ax.set_xlabel("Wavenumber (cm⁻¹)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_xlim(xlim)
        ax.set_title("FTIR Spectrum")
        ax.invert_xaxis()  # IR spectra usually have high to low wavenumber
        ax.grid(True)
        st.pyplot(fig)

