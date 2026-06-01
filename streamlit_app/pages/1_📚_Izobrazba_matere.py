import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Izobrazba matere", page_icon="📚", layout="wide")

BARVE = {
    "olive":  "#8CB369",
    "gold":   "#F4E285",
    "brown":  "#F4A259",
    "teal":   "#5B8E7D",
    "brick":  "#BC4B51",
}

BASE = Path(__file__).parent.parent

@st.cache_data
def nalozi_podatke():
    pot = "../../data/raw/csv/izobrazba_prvi_otrok.csv"
    df = pd.read_csv(pot, sep=';', encoding='cp1250', skiprows=2)
    df = df.replace("...", np.nan)
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.columns = [col if i < 2 else col[:4] for i, col in enumerate(df.columns)]
    return df

st.title("📚 Prvo rojstvo po izobrazbi matere")
st.caption("Analiza števila prvih rojstev glede na izobrazbo matere v Sloveniji")

try:
    podatki = nalozi_podatke()

    # --- Graf 1: Izobrazba ---
    izobrazba = podatki[
        (podatki["STAROSTNE SKUPINE"] == "Starostne skupine - SKUPAJ") &
        (podatki["IZOBRAZBA MATERE"].isin([
            "Osnovnošolska ali nižja - skupaj",
            "Srednješolska - skupaj",
            "Višješolska in visokošolska - skupaj"
        ]))
    ]

    izobrazba_t = izobrazba.iloc[:, 2:].T
    izobrazba_t.columns = izobrazba["IZOBRAZBA MATERE"].values

    colors_list = [BARVE["brick"], BARVE["teal"], BARVE["brown"]]

    fig1 = go.Figure()
    for i, col in enumerate(izobrazba_t.columns):
        fig1.add_trace(go.Scatter(
            x=izobrazba_t.index,
            y=izobrazba_t[col],
            mode='lines+markers',
            name=col,
            line=dict(color=colors_list[i], width=2.5),
            marker=dict(size=6),
            hovertemplate=f"<b>{col}</b><br>Leto: %{{x}}<br>Rojstev: %{{y:,.0f}}<extra></extra>"
        ))

    fig1.update_layout(
        title="Prvo rojstvo po izobrazbi matere",
        xaxis_title="Leto",
        yaxis_title="Število rojstev",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=480,
        hovermode="x unified"
    )
    fig1.update_xaxes(tickangle=45)

    st.plotly_chart(fig1, use_container_width=True)

    # --- Tabela s povprečji ---
    st.markdown("### 📊 Povprečne vrednosti po kategorijah")
    povprecja = izobrazba_t.mean().sort_values(ascending=False).reset_index()
    povprecja.columns = ["Izobrazba matere", "Povprečno število rojstev"]
    povprecja["Povprečno število rojstev"] = povprecja["Povprečno število rojstev"].round(1)
    st.dataframe(povprecja, use_container_width=True, hide_index=True)

    # --- Graf 2: Skupni trend ---
    st.markdown("### 📈 Skupni letni trend (vsa izobrazbena stopnja)")
    skupaj = podatki[
        (podatki["STAROSTNE SKUPINE"] == "Starostne skupine - SKUPAJ") &
        (podatki["IZOBRAZBA MATERE"] == "Izobrazba matere - SKUPAJ")
    ]

    letni_trend = skupaj.iloc[0, 2:].reset_index()
    letni_trend.columns = ['leto', 'stevilo']
    letni_trend['leto'] = letni_trend['leto'].str.extract(r'(\d{4})').astype(int)
    letni_trend = letni_trend.dropna()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=letni_trend['leto'],
        y=letni_trend['stevilo'],
        mode='lines+markers',
        line=dict(color=BARVE["brick"], width=3),
        marker=dict(size=8, color=BARVE["brick"]),
        fill='tozeroy',
        fillcolor='rgba(188,75,81,0.12)',
        hovertemplate="Leto: %{x}<br>Rojstev: %{y:,.0f}<extra></extra>"
    ))
    fig2.update_layout(
        title="Prva rojstva v Sloveniji (2010–2024)",
        xaxis_title="Leto",
        yaxis_title="Število rojstev",
        template="plotly_white",
        height=380,
    )

    st.plotly_chart(fig2, use_container_width=True)

except FileNotFoundError:
    st.error("Datoteka `data/raw/csv/izobrazba_prvi_otrok.csv` ni bila najdena. Preveri pot do podatkov.")
except Exception as e:
    st.error(f"Napaka pri branju podatkov: {e}")
