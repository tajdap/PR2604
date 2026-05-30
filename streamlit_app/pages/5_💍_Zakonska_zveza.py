import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import re
from pathlib import Path

st.set_page_config(page_title="Zakonska zveza", page_icon="💍", layout="wide")

BARVE = {
    "brick":  "#BC4B51",
    "teal":   "#5B8E7D",
    "olive":  "#8CB369",
    "gold":   "#F4E285",
    "brown":  "#F4A259",
}

BASE = Path(__file__).parent.parent

def izvleci_stevilko(v):
    if pd.isna(v): return np.nan
    s = re.sub(r'[^\d,.]', '', str(v))
    if not s: return np.nan
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif '.' in s and len(s.split('.')[-1]) == 3:
        s = s.replace('.', '')
    else:
        s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return np.nan

@st.cache_data
def nalozi_podatke():
    pot = "../data/raw/csv/rojstva_zakonske_zveze.csv"
    df = pd.read_csv(pot, encoding="cp1250", sep=";", skiprows=1)
    df.columns = ["Leto", "Starostne skupine", "Rojeni v zakonski zvezi", "Rojeni zunaj zakonske zveze"]
    df["Leto"] = pd.to_numeric(df["Leto"], errors="coerce")
    for col in ["Rojeni v zakonski zvezi", "Rojeni zunaj zakonske zveze"]:
        df[col] = df[col].apply(lambda x: izvleci_stevilko(x) if isinstance(x, str) else x)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Leto"])
    df["Leto"] = df["Leto"].astype(int)
    return df

st.title("💍 Rojstva v in izven zakonske zveze")
st.caption("Primerjava rojstev znotraj in zunaj zakonske zveze skozi leta")

try:
    ratings = nalozi_podatke()

    skupaj = ratings[ratings['Starostne skupine'] == 'Starostne skupine - SKUPAJ'].copy()

    # --- KPI ---
    zadnje = skupaj.dropna(subset=['Rojeni v zakonski zvezi', 'Rojeni zunaj zakonske zveze'])
    if not zadnje.empty:
        zadnja_vrstica = zadnje.iloc[-1]
        skupaj_rojstev = zadnja_vrstica['Rojeni v zakonski zvezi'] + zadnja_vrstica['Rojeni zunaj zakonske zveze']
        delez_zunaj = zadnja_vrstica['Rojeni zunaj zakonske zveze'] / skupaj_rojstev * 100 if skupaj_rojstev > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Zadnje leto", int(zadnja_vrstica['Leto']))
        col2.metric("V zakonski zvezi", f"{int(zadnja_vrstica['Rojeni v zakonski zvezi']):,}")
        col3.metric("Zunaj zakonske zveze", f"{int(zadnja_vrstica['Rojeni zunaj zakonske zveze']):,}")
        col4.metric("Delež zunaj z.z.", f"{delez_zunaj:.1f} %")

    st.markdown("---")

    # --- Linijski graf ---
    st.subheader("📈 Trend rojstev skozi leta")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=skupaj['Leto'], y=skupaj['Rojeni v zakonski zvezi'],
        mode='lines+markers', name='V zakonski zvezi',
        line=dict(color=BARVE["teal"], width=2.5),
        marker=dict(size=6),
        hovertemplate="Leto: %{x}<br>V zakonski zvezi: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=skupaj['Leto'], y=skupaj['Rojeni zunaj zakonske zveze'],
        mode='lines+markers', name='Zunaj zakonske zveze',
        line=dict(color=BARVE["brick"], width=2.5),
        marker=dict(size=6),
        hovertemplate="Leto: %{x}<br>Zunaj zakonske zveze: %{y:,.0f}<extra></extra>"
    ))

    fig.update_layout(
        title='Rojstva v in izven zakonske zveze skozi leta',
        xaxis_title='Leto', yaxis_title='Število rojstev',
        template='plotly_white', height=450,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Stacked area ---
    st.subheader("📊 Delež rojstev — normiran prikaz")
    skupaj_clean = skupaj.dropna(subset=['Rojeni v zakonski zvezi', 'Rojeni zunaj zakonske zveze']).copy()
    skupaj_clean['skupaj'] = skupaj_clean['Rojeni v zakonski zvezi'] + skupaj_clean['Rojeni zunaj zakonske zveze']
    skupaj_clean['p_zz'] = skupaj_clean['Rojeni v zakonski zvezi'] / skupaj_clean['skupaj'] * 100
    skupaj_clean['p_zunaj'] = skupaj_clean['Rojeni zunaj zakonske zveze'] / skupaj_clean['skupaj'] * 100

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=skupaj_clean['Leto'], y=skupaj_clean['p_zz'],
        name='V zakonski zvezi (%)', marker_color=BARVE["teal"],
        hovertemplate="Leto: %{x}<br>V z.z.: %{y:.1f}%<extra></extra>"
    ))
    fig2.add_trace(go.Bar(
        x=skupaj_clean['Leto'], y=skupaj_clean['p_zunaj'],
        name='Zunaj zakonske zveze (%)', marker_color=BARVE["brick"],
        hovertemplate="Leto: %{x}<br>Zunaj z.z.: %{y:.1f}%<extra></extra>"
    ))
    fig2.update_layout(
        barmode='stack',
        title='Delež rojstev v/izven zakonske zveze (%)',
        xaxis_title='Leto', yaxis_title='Delež (%)',
        yaxis=dict(range=[0, 100]),
        template='plotly_white', height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Po starostnih skupinah ---
    if 'Starostne skupine' in ratings.columns:
        st.subheader("👥 Primerjava po starostnih skupinah")
        starost_skupine = ratings[ratings['Starostne skupine'] != 'Starostne skupine - SKUPAJ']['Starostne skupine'].unique()
        izbrana_skupina = st.selectbox("Izberi starostno skupino:", starost_skupine)

        df_sk = ratings[ratings['Starostne skupine'] == izbrana_skupina].copy()
        df_sk = df_sk.dropna(subset=['Rojeni v zakonski zvezi', 'Rojeni zunaj zakonske zveze'])

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_sk['Leto'], y=df_sk['Rojeni v zakonski zvezi'],
            mode='lines+markers', name='V zakonski zvezi',
            line=dict(color=BARVE["teal"], width=2)
        ))
        fig3.add_trace(go.Scatter(
            x=df_sk['Leto'], y=df_sk['Rojeni zunaj zakonske zveze'],
            mode='lines+markers', name='Zunaj zakonske zveze',
            line=dict(color=BARVE["brick"], width=2)
        ))
        fig3.update_layout(
            title=f'Starostna skupina: {izbrana_skupina}',
            xaxis_title='Leto', yaxis_title='Število rojstev',
            template='plotly_white', height=380,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig3, use_container_width=True)

except FileNotFoundError:
    st.error("❌ Datoteka `data/raw/csv/rojstva_zakonske_zveze.csv` ni bila najdena.")
except Exception as e:
    st.error(f"Napaka pri branju podatkov: {e}")