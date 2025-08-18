import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(page_title="RDG Scatter Plot", layout="wide")

st.title("RDG Scatter / Density Plot Viewer")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload Multiwfn output file (e.g., output.txt)", type=["txt", "dat"])

# --- Sidebar controls ---
plot_mode = st.sidebar.radio("Plot type", ["Scatter", "Hexbin"])
xmin = st.sidebar.slider("X min (sign(λ₂)ρ)", -0.1, 0.0, -0.05, 0.005)
xmax = st.sidebar.slider("X max (sign(λ₂)ρ)", 0.0, 0.1, 0.05, 0.005)
ymax = st.sidebar.slider("Y max (RDG)", 0.5, 5.0, 2.0, 0.1)

point_size = st.sidebar.slider("Point size (scatter)", 1, 20, 5)
gridsize = st.sidebar.slider("Hexbin grid size", 50, 300, 150)

# --- Main plot ---
if uploaded_file is not None:
    data = np.loadtxt(uploaded_file, usecols=(3, 4))
    x = data[:, 0]  # col4: sign(λ₂)ρ
    y = data[:, 1]  # col5: RDG

    # --- Custom colormap (blue-green-red) for scatter ---
    colors_list = [(0, 0, 1), (0, 1, 0), (1, 0, 0)]
    positions = [0, 0.6142857, 1]  # normalized mapping of -0.035, -0.0075, 0.02
    cmap = LinearSegmentedColormap.from_list("custom_cmap", list(zip(positions, colors_list)))

    fig, ax = plt.subplots(figsize=(10, 6))

    if plot_mode == "Scatter":
        sc = ax.scatter(x, y, c=x, cmap=cmap, s=point_size, edgecolors="none")
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label(r"sign($\lambda_2$)$\rho$ (a.u.)", fontsize=14)
        cbar.set_ticks(np.arange(-0.035, 0.021, 0.01))
        cbar.formatter = plt.FormatStrFormatter("%.3f")
        cbar.update_ticks()
        sc.set_clim(-0.035, 0.02)

    elif plot_mode == "Hexbin":
        hb = ax.hexbin(x, y, gridsize=gridsize, cmap="viridis", bins="log",
                       extent=(xmin, xmax, 0, ymax))
        cbar = plt.colorbar(hb, ax=ax)
        cbar.set_label("log(counts)", fontsize=14)

    # Axis settings
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.0, ymax)
    ax.set_xlabel(r"sign($\lambda_2$)$\rho$ (a.u.)", fontsize=16)
    ax.set_ylabel("RDG", fontsize=16)
    ax.tick_params(axis="x", rotation=45)
    for spine in ax.spines.values():
        spine.set_linewidth(2)

    st.pyplot(fig)

    # --- Save PNG download ---
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button(
        label="Download plot as PNG",
        data=buf.getvalue(),
        file_name=f"RDGscatter_{plot_mode.lower()}.png",
        mime="image/png"
    )

else:
    st.info("👆 Upload a Multiwfn output file (output.txt with at least 5 columns).")
