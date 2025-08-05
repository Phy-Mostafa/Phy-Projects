import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import re

# ========== Title ==========
st.title("UV-Vis Spectrum Plotter from Gaussian Output")
st.markdown("Upload a Gaussian TD-DFT output file (.log or .out) to generate the UV-Vis absorption spectrum.")

# ========== File Upload ==========
uploaded_file = st.file_uploader("Choose a Gaussian output file", type=["log", "out"])

# ========== Functions ==========

def extract_uv_data(content):
    """
    Extract excited state wavelengths and oscillator strengths from Gaussian output.
    Returns two arrays: wavelengths (nm) and oscillator strengths.
    """
    wavelengths = []
    osc_strengths = []

    lines = content.splitlines()
    for line in lines:
        if "Excited State" in line and "f=" in line:
            # Example line: Excited State   1:   Singlet-A      4.1234 eV  300.7 nm  f=0.1234
            parts = line.split()
            try:
                wavelength = float(parts[6])
                f_value = float([x for x in parts if x.startswith("f=")][0][2:])
                wavelengths.append(wavelength)
                osc_strengths.append(f_value)
            except (IndexError, ValueError):
                continue

    return np.array(wavelengths), np.array(osc_strengths)

def gaussian_broadening(wavelengths, intensities, fwhm=0.3, resolution=0.2):
    """
    Apply Gaussian broadening to the stick spectrum in wavelength domain.
    """
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    x = np.arange(min(wavelengths) - 50, max(wavelengths) + 50, resolution)
    y = np.zeros_like(x)

    for wl, inten in zip(wavelengths, intensities):
        y += inten * np.exp(-((x - wl) ** 2) / (2 * sigma ** 2))

    return x, y

# ========== Main Logic ==========

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    wavelengths, osc_strengths = extract_uv_data(content)

    if len(wavelengths) == 0:
        st.error("No TD-DFT excited states found.")
    else:
        st.success(f"Extracted {len(wavelengths)} excited states.")

        # === Controls ===
        fwhm = st.slider("Gaussian Broadening (FWHM, nm)", 0.1, 20.0, 0.5, step=0.5)
        wl_range = st.slider("Wavelength Range (nm)", 100, 800, (200, 600))
        show_sticks = st.checkbox("Show stick spectrum", value=True)

        x, y = gaussian_broadening(wavelengths, osc_strengths, fwhm=fwhm)

        # === Plot ===
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(x, y, label="Simulated spectrum", color='blue')

        if show_sticks:
            for wl, inten in zip(wavelengths, osc_strengths):
                if wl_range[0] <= wl <= wl_range[1]:
                    ax.vlines(wl, 0, inten, colors='red', linestyles='dotted', linewidth=1)

        ax.set_xlim(wl_range[::-1])  # Invert x-axis: UV to visible
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title("UV-Vis Absorption Spectrum")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
