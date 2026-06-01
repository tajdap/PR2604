import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import urllib.request
from pathlib import Path

st.set_page_config(page_title="Plače po občinah", page_icon="💰", layout="wide")

SLO_BRUTO_2023 = 2254.86
BASE = Path(__file__).parent.parent
BASE_DIR = Path(__file__).resolve().parents[2]
def normalize_name(name):
    if not isinstance(name, str):
        return name
    if '/' in name:
        name = name.split('/')[0].strip()
    name = name.replace(' - ', '-')
    name = name.replace('Slov. goricah', 'Slovenskih goricah')
    return name

@st.cache_data
def nalozi_placo():
    df = pd.read_csv(BASE_DIR / "data" / "raw" / "csv" / "obcine_avg_placa.csv",
                     encoding='cp1250', sep=';', skiprows=2,
                     decimal='.', na_values=['z'])
    df.columns = ['obcina', 'bruto_2023', 'bruto_2024', 'bruto_2025',
                  'neto_2023', 'neto_2024', 'neto_2025']
    df = df[df['obcina'] != 'SLOVENIJA'].copy()
    df['obcina_norm'] = df['obcina'].apply(normalize_name)
    for col in ['bruto_2023', 'bruto_2024', 'neto_2023', 'neto_2024']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

@st.cache_data
def nalozi_geojson():
    url = 'https://raw.githubusercontent.com/stefanb/gurs-rpe/master/data/OB.geojson'
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            geo = json.loads(resp.read())
        for feat in geo['features']:
            feat['id'] = normalize_name(feat['properties']['OB_UIME'])
        return geo
    except Exception:
        return None

st.title("💰 Povprečne plače po občinah")
st.caption("Interaktivni zemljevid povprečnih bruto in neto plač po slovenskih občinah (2023)")

try:
    df_placa = nalozi_placo()

    # --- KPI vrstica ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Število občin", df_placa['bruto_2023'].notna().sum())
    col2.metric("SLO povprečje bruto", f"{SLO_BRUTO_2023:,.0f} €")
    col3.metric("Najvišja bruto plača", f"{df_placa['bruto_2023'].max():,.0f} €")
    col4.metric("Najnižja bruto plača", f"{df_placa['bruto_2023'].min():,.0f} €")

    st.markdown("---")

    # --- Izbira: bruto ali neto ---
    tip_place = st.radio("Prikaži:", ["Bruto plača 2023", "Neto plača 2023"], horizontal=True)
    col_map = 'bruto_2023' if 'Bruto' in tip_place else 'neto_2023'
    slo_ref = SLO_BRUTO_2023 if 'Bruto' in tip_place else 1478.0  # SLO neto 2023 approx

    geo_data = nalozi_geojson()

    if geo_data is None:
        st.warning("⚠️ Ni mogoče naložiti GeoJSON-a (ni internetne povezave). Prikazujem tabelo.")
        prikaz = df_placa[['obcina', 'bruto_2023', 'neto_2023']].dropna().sort_values('bruto_2023', ascending=False)
        prikaz.columns = ['Občina', 'Bruto 2023 (€)', 'Neto 2023 (€)']
        st.dataframe(prikaz, use_container_width=True, hide_index=True)
    else:
        fig_map = go.Figure(go.Choroplethmap(
            geojson=geo_data,
            locations=df_placa['obcina_norm'],
            z=df_placa[col_map],
            customdata=df_placa[['obcina', 'bruto_2023', 'neto_2023']].values,
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                'Bruto plača 2023: %{customdata[1]:,.0f} €<br>'
                'Neto plača 2023: %{customdata[2]:,.0f} €'
                '<extra></extra>'
            ),
            colorscale=[
                [0.00, '#4B1248'],
                [0.25, '#BC4B51'],
                [0.50, '#F4A259'],
                [0.75, '#8CB369'],
                [1.00, '#1B4332'],
            ],
            zmid=slo_ref,
            colorbar=dict(
                title=dict(text=tip_place.replace(' 2023', '<br>2023 (€)'), font=dict(size=11)),
                tickformat=',.0f',
                len=0.75,
                thickness=14,
            ),
            marker_line_color='white',
            marker_line_width=0.5,
            marker_opacity=0.9,
        ))
        fig_map.update_layout(
            title=dict(
                text=f'{tip_place} po občinah v Sloveniji (2023)<br>'
                     f'<sup>Slovensko povprečje: {slo_ref:,.0f} € − srednja barva na lestvici</sup>',
                x=0.5, xanchor='center', font=dict(size=14)
            ),
            map=dict(style='carto-positron', center=dict(lat=46.12, lon=14.82), zoom=7.0),
            margin=dict(l=10, r=10, t=90, b=10),
            height=620
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # --- Tabela ---
    with st.expander("📋 Prikaži tabelo vseh občin"):
        prikaz = df_placa[['obcina', 'bruto_2023', 'neto_2023']].dropna(subset=['bruto_2023']).copy()
        prikaz.columns = ['Občina', 'Bruto 2023 (€)', 'Neto 2023 (€)']
        prikaz = prikaz.sort_values('Bruto 2023 (€)', ascending=False)
        prikaz['Bruto 2023 (€)'] = prikaz['Bruto 2023 (€)'].round(0)
        prikaz['Neto 2023 (€)'] = prikaz['Neto 2023 (€)'].round(0)
        st.dataframe(prikaz, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"❌ Datoteka ni bila najdena: {e}\n\nPreveri, da je datoteka v `data/raw/csv/`.")
except Exception as e:
    st.error(f"Napaka: {e}")
