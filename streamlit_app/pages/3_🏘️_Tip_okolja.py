import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import urllib.request
from pathlib import Path

st.set_page_config(page_title="Tip okolja", page_icon="🏘️", layout="wide")

BARVE = ["#8CB369", "#F4E285", "#F4A259", "#5B8E7D", "#BC4B51"]
BASE = Path(__file__).parent.parent

def extract_num(v):
    if pd.isna(v): return 0.0
    s = str(v).replace('"', '').strip()
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif '.' in s and len(s.split('.')[-1]) == 3:
        s = s.replace('.', '')
    else:
        s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

def norm_ime(i):
    return str(i).lower().replace('"', '').replace(' ', '').replace('-', '').strip()

def normalize_name_geo(name):
    if not isinstance(name, str):
        return name
    if '/' in name:
        name = name.split('/')[0].strip()
    name = name.replace(' - ', '-')
    name = name.replace('Slov. goricah', 'Slovenskih goricah')
    return name

@st.cache_data
def nalozi_podatke():
    df_rodnost = pd.read_csv("../data/raw/csv/obcine_rodnost.csv",
                             sep=';', encoding='cp1250', skiprows=2)
    df_gostota = pd.read_csv("../data/raw/csv/gostota_obcine.csv",
                             sep=';', encoding='cp1250', skiprows=2)

    df_rodnost.columns = [c.replace('"', '').strip() for c in df_rodnost.columns]
    df_gostota.columns = [c.replace('"', '').strip() for c in df_gostota.columns]

    obcina_col_rodnost = [c for c in df_rodnost.columns if 'OBČINE' in c.upper()][0]
    obcina_col_gostota = [c for c in df_gostota.columns if 'OBČINE' in c.upper() or 'OBČINA' in c.upper()][0]

    df_rodnost['Kljuc'] = df_rodnost[obcina_col_rodnost].apply(norm_ime)
    df_gostota['Kljuc'] = df_gostota[obcina_col_gostota].apply(norm_ime)
    df_rodnost = df_rodnost[df_rodnost['Kljuc'] != 'slovenija']

    gostota_col = [c for c in df_gostota.columns if '2023' in c][0]
    df_gostota_clean = df_gostota[[obcina_col_gostota, gostota_col, 'Kljuc']].copy()
    df_gostota_clean.columns = ['Obcina', 'Surova_Vrednost', 'Kljuc']

    df_rodnost_final = df_rodnost.rename(columns={obcina_col_rodnost: 'Obcina'})
    df_merge = pd.merge(df_rodnost_final, df_gostota_clean[['Kljuc', 'Surova_Vrednost']], on='Kljuc')

    df_merge['Gostota_Num'] = df_merge['Surova_Vrednost'].apply(extract_num)
    df_merge['_gostota_raw'] = df_merge['Gostota_Num']
    df_merge['Obcina_Geo'] = df_merge['Obcina'].apply(normalize_name_geo)

    leta_07_12 = [f"{l} Živorojeni na 1.000 prebivalcev" for l in range(2007, 2013)]
    leta_13_18 = [f"{l} Živorojeni na 1.000 prebivalcev" for l in range(2013, 2019)]
    leta_19_23 = [f"{l} Živorojeni na 1.000 prebivalcev" for l in range(2019, 2024)]

    def povprecje(row, leta):
        vrednosti = [extract_num(row[l]) for l in leta if l in row]
        return sum(vrednosti) / len(vrednosti) if vrednosti else 0.0

    df_merge['2007-2012'] = df_merge.apply(lambda r: povprecje(r, leta_07_12), axis=1)
    df_merge['2013-2018'] = df_merge.apply(lambda r: povprecje(r, leta_13_18), axis=1)
    df_merge['2019-2023'] = df_merge.apply(lambda r: povprecje(r, leta_19_23), axis=1)

    return df_merge

@st.cache_data
def nalozi_geojson():
    url = 'https://raw.githubusercontent.com/stefanb/gurs-rpe/master/data/OB.geojson'
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            geo = json.loads(resp.read())
        for feat in geo['features']:
            feat['id'] = normalize_name_geo(feat['properties']['OB_UIME'])
        return geo
    except Exception:
        return None

st.title("🏘️ Rodnost glede na tip okolja")
st.caption("Primerjava rodnosti med mestnim in podeželskim okoljem po obdobjih (2007–2023)")

try:
    df_merge = nalozi_podatke()

    # --- Slider ---
    mejnik = st.slider(
        "Mejnik gostote (preb./km²) za mestno/podeželsko razvrstitev:",
        min_value=50, max_value=500, value=200, step=10
    )

    df_merge['Tip_Okolja'] = df_merge['_gostota_raw'].apply(
        lambda g: f'Mestno ({mejnik}+)' if g > mejnik else f'Podeželje (do {mejnik})'
    )

    mestno = df_merge[df_merge['Tip_Okolja'].str.startswith('Mestno')]
    podezelje = df_merge[df_merge['Tip_Okolja'].str.startswith('Podeželje')]

    col1, col2 = st.columns(2)
    col1.metric("Mestnih občin", len(mestno))
    col2.metric("Podeželskih občin", len(podezelje))

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["🗺️ Zemljevid rodnosti", "📊 Primerjava po obdobjih", "📦 Porazdelitev"])

    # ── TAB 1: Choropleth ────────────────────────────────────────────
    with tab1:
        st.subheader("Rodnost po občinah — zemljevid")

        obdobje_zem = st.selectbox("Izberi obdobje:", ['2019-2023', '2013-2018', '2007-2012'])

        geo_data = nalozi_geojson()

        df_map = df_merge[['Obcina', 'Obcina_Geo', 'Tip_Okolja', '_gostota_raw', obdobje_zem]].copy()
        df_map = df_map[df_map[obdobje_zem] > 0]

        if geo_data is None:
            st.warning("⚠️ Ni mogoče naložiti GeoJSON-a. Prikazujem tabelo.")
            st.dataframe(df_map[['Obcina', 'Tip_Okolja', obdobje_zem]].sort_values(obdobje_zem, ascending=False),
                         use_container_width=True, hide_index=True)
        else:
            # Barva glede na tip okolja ali vrednost rodnosti
            prikaz_tip = st.radio("Obarvanost:", ["Po vrednosti rodnosti", "Po tipu okolja"], horizontal=True)

            if prikaz_tip == "Po vrednosti rodnosti":
                fig_map = go.Figure(go.Choroplethmap(
                    geojson=geo_data,
                    locations=df_map['Obcina_Geo'],
                    z=df_map[obdobje_zem],
                    customdata=df_map[['Obcina', 'Tip_Okolja', '_gostota_raw', obdobje_zem]].values,
                    hovertemplate=(
                        '<b>%{customdata[0]}</b><br>'
                        'Tip: %{customdata[1]}<br>'
                        'Gostota: %{customdata[2]:.0f} preb./km²<br>'
                        f'Rodnost ({obdobje_zem}): %{{customdata[3]:.2f}}'
                        '<extra></extra>'
                    ),
                    colorscale=[
                        [0.00, '#4B1248'],
                        [0.33, '#BC4B51'],
                        [0.66, '#F4A259'],
                        [1.00, '#8CB369'],
                    ],
                    colorbar=dict(
                        title=dict(text=f'Rodnost<br>{obdobje_zem}', font=dict(size=11)),
                        len=0.75, thickness=14,
                    ),
                    marker_line_color='white',
                    marker_line_width=0.5,
                    marker_opacity=0.9,
                ))
            else:
                # Mestno = #BC4B51, Podeželje = #8CB369
                df_map['tip_num'] = df_map['Tip_Okolja'].apply(lambda x: 1 if x.startswith('Mestno') else 0)
                fig_map = go.Figure(go.Choroplethmap(
                    geojson=geo_data,
                    locations=df_map['Obcina_Geo'],
                    z=df_map['tip_num'],
                    customdata=df_map[['Obcina', 'Tip_Okolja', '_gostota_raw', obdobje_zem]].values,
                    hovertemplate=(
                        '<b>%{customdata[0]}</b><br>'
                        'Tip: %{customdata[1]}<br>'
                        'Gostota: %{customdata[2]:.0f} preb./km²<br>'
                        f'Rodnost ({obdobje_zem}): %{{customdata[3]:.2f}}'
                        '<extra></extra>'
                    ),
                    colorscale=[[0, '#8CB369'], [1, '#BC4B51']],
                    showscale=False,
                    marker_line_color='white',
                    marker_line_width=0.5,
                    marker_opacity=0.85,
                ))
                # Legenda ročno
                st.markdown(
                    f'<span style="color:#BC4B51;">⬛</span> Mestno ({mejnik}+)&nbsp;&nbsp;&nbsp;'
                    f'<span style="color:#8CB369;">⬛</span> Podeželje (do {mejnik})',
                    unsafe_allow_html=True
                )

            fig_map.update_layout(
                title=dict(
                    text=f'Rodnost po občinah — {obdobje_zem}',
                    x=0.5, xanchor='center', font=dict(size=14)
                ),
                map=dict(style='carto-positron', center=dict(lat=46.12, lon=14.82), zoom=7.0),
                margin=dict(l=10, r=10, t=60, b=10),
                height=600
            )
            st.plotly_chart(fig_map, use_container_width=True)

    # ── TAB 2: Grouped bar ───────────────────────────────────────────
    with tab2:
        st.subheader("Povprečna rodnost po obdobjih in tipu okolja")

        obdobja = ['2007-2012', '2013-2018', '2019-2023']
        df_long = df_merge.melt(
            id_vars=['Obcina', 'Tip_Okolja'],
            value_vars=obdobja,
            var_name='Obdobje', value_name='Rodnost'
        )
        df_long = df_long[df_long['Rodnost'] > 0]
        povp = df_long.groupby(['Obdobje', 'Tip_Okolja'])['Rodnost'].mean().reset_index()

        tipi = povp['Tip_Okolja'].unique()
        barve_tipi = [BARVE[0], BARVE[4]]

        fig = go.Figure()
        for i, tip in enumerate(tipi):
            d = povp[povp['Tip_Okolja'] == tip]
            fig.add_trace(go.Bar(
                x=d['Obdobje'], y=d['Rodnost'],
                name=tip,
                marker_color=barve_tipi[i % 2],
                marker_line_color='white', marker_line_width=0.8,
                error_y=dict(
                    type='data',
                    array=df_long[df_long['Tip_Okolja'] == tip].groupby('Obdobje')['Rodnost'].std().reindex(d['Obdobje']).values,
                    visible=True, color='rgba(0,0,0,0.3)'
                ),
                hovertemplate=f"<b>{tip}</b><br>Obdobje: %{{x}}<br>Rodnost: %{{y:.2f}}<extra></extra>"
            ))

        fig.update_layout(
            barmode='group',
            title='Povprečna rodnost glede na tip okolja (2007–2023)',
            xaxis_title='Obdobje', yaxis_title='Živorojeni na 1.000 prebivalcev',
            yaxis=dict(range=[6.5, 12]),
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 3: Box plot ──────────────────────────────────────────────
    with tab3:
        st.subheader("Porazdelitev rodnosti po tipu okolja")

        obdobja = ['2007-2012', '2013-2018', '2019-2023']
        df_long2 = df_merge.melt(
            id_vars=['Obcina', 'Tip_Okolja'],
            value_vars=obdobja,
            var_name='Obdobje', value_name='Rodnost'
        )
        df_long2 = df_long2[df_long2['Rodnost'] > 0]

        fig_box = px.box(
            df_long2, x='Obdobje', y='Rodnost', color='Tip_Okolja',
            color_discrete_sequence=[BARVE[0], BARVE[4]],
            points='outliers',
            title='Porazdelitev rodnosti po občinah in tipu okolja'
        )
        fig_box.update_layout(template='plotly_white', height=420,
                              legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
        st.plotly_chart(fig_box, use_container_width=True)

    # --- Tabela ---
    with st.expander("📋 Prikaži podatke po občinah"):
        prikaz = df_merge[['Obcina', 'Tip_Okolja', '_gostota_raw', '2007-2012', '2013-2018', '2019-2023']].copy()
        prikaz.columns = ['Občina', 'Tip okolja', 'Gostota (preb./km²)', '2007-2012', '2013-2018', '2019-2023']
        prikaz = prikaz[prikaz['2019-2023'] > 0].sort_values('2019-2023', ascending=False)
        for col in ['2007-2012', '2013-2018', '2019-2023']:
            prikaz[col] = prikaz[col].round(2)
        prikaz['Gostota (preb./km²)'] = prikaz['Gostota (preb./km²)'].round(1)
        st.dataframe(prikaz, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"❌ Datoteka ni bila najdena: {e}")
except Exception as e:
    st.error(f"Napaka pri branju podatkov: {e}")
