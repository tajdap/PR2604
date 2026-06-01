import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Starost matere", page_icon="👩", layout="wide")

BARVE = {
    "brick":   "#BC4B51",
    "brown":   "#F4A259",
    "gold":    "#F4E285",
    "olive":   "#8CB369",
    "teal":    "#5B8E7D",
    "gray1":   "#999999",
    "gray2":   "#555555",
}

BASE = Path(__file__).parent.parent
BASE_DIR = Path(__file__).resolve().parents[2]
@st.cache_data
def nalozi_podatke():
    pot = BASE_DIR / "data" / "raw" / "csv" / "izobrazba_prvi_otrok.csv"
    df = pd.read_csv(pot, sep=';', encoding='cp1250', skiprows=2)
    df = df.replace("...", np.nan)
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.columns = [col if i < 2 else col[:4] for i, col in enumerate(df.columns)]
    return df

st.title("👩 Prvo rojstvo po starosti matere")
st.caption("Trendi prvih rojstev razčlenjeni po starostnih skupinah mater")

try:
    podatki = nalozi_podatke()

    starost = podatki[podatki["IZOBRAZBA MATERE"] == "Izobrazba matere - SKUPAJ"]
    starost_t = starost.iloc[:, 2:].T
    starost_t.columns = starost["STAROSTNE SKUPINE"].values

    colors_starost = [
        BARVE["brick"],
        BARVE["brown"],
        BARVE["gold"],
        BARVE["olive"],
        BARVE["teal"],
        BARVE["gray1"],
        BARVE["gray2"],
    ]

    # --- Filter ---
    vse_skupine = list(starost_t.columns)
    izbrane = st.multiselect(
        "Izberi starostne skupine:",
        options=vse_skupine,
        default=vse_skupine
    )

    if not izbrane:
        st.warning("Izberi vsaj eno starostno skupino.")
    else:
        fig = go.Figure()
        for i, col in enumerate(starost_t.columns):
            if col not in izbrane:
                continue
            fig.add_trace(go.Scatter(
                x=starost_t.index,
                y=starost_t[col],
                mode='lines+markers',
                name=col,
                line=dict(color=colors_starost[i % len(colors_starost)], width=2.5),
                marker=dict(size=6),
                hovertemplate=f"<b>{col}</b><br>Leto: %{{x}}<br>Rojstev: %{{y:,.0f}}<extra></extra>"
            ))

        fig.update_layout(
            title="Prvo rojstvo po starosti matere",
            xaxis_title="Leto",
            yaxis_title="Število rojstev",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template="plotly_white",
            height=500,
            hovermode="x unified"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # --- Povprečja ---
    st.markdown("### 📊 Povprečje po starostnih skupinah (vsa leta)")
    povprecja = starost_t.mean().sort_values(ascending=False).reset_index()
    povprecja.columns = ["Starostna skupina", "Povprečno število rojstev"]
    povprecja["Povprečno število rojstev"] = povprecja["Povprečno število rojstev"].round(1)

    col1, col2 = st.columns([2, 1])
    with col1:
        fig_bar = go.Figure(go.Bar(
            x=povprecja["Povprečno število rojstev"],
            y=povprecja["Starostna skupina"],
            orientation='h',
            marker_color=[colors_starost[i % len(colors_starost)] for i in range(len(povprecja))],
            hovertemplate="%{y}: %{x:,.1f}<extra></extra>"
        ))
        fig_bar.update_layout(
            title="Povprečno število rojstev po starostni skupini",
            xaxis_title="Povprečno število rojstev",
            template="plotly_white",
            height=360,
            margin=dict(l=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.dataframe(povprecja, use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.error("❌ Datoteka `data/raw/csv/izobrazba_prvi_otrok.csv` ni bila najdena.")
except Exception as e:
    st.error(f"Napaka pri branju podatkov: {e}")
