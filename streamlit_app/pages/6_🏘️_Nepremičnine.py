import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium
import branca.colormap as cm
import json
import re
import unicodedata

st.set_page_config(
    page_title="Analiza nepremičnin po občinah",
    page_icon="🏠",
    layout="wide"
)

# NALAGANJE PODATKOV
BASE = Path(__file__).parent.parent
BASE_DIR = Path(__file__).resolve().parents[2]
@st.cache_data
def load_data():

    poskus = pd.read_csv(
        BASE_DIR / "data" / "raw" / "csv" / "poskus.csv",
        encoding="utf-8",
        usecols=[
            "ID_POSLA",
            "OBCINA",
            "VRSTA_DELA_STAVBE",
            "PRODANA_POVRSINA",
            "POGODBENA_CENA_DELA_STAVBE",
        ]
    )

    posli = pd.read_csv(
        BASE_DIR / "data" / "raw" / "csv" / "posli.csv",
        encoding="utf-8",
        usecols=[
            "ID_POSLA",
            "POGODBENA_CENA_ODSKODNINA",
            "TRZNOST_POSLA",
        ]
    )

    df = poskus.merge(
        posli,
        on="ID_POSLA",
        how="left"
    )

    df["CENA"] = df["POGODBENA_CENA_DELA_STAVBE"].combine_first(
        df["POGODBENA_CENA_ODSKODNINA"]
    )

    df = df.rename(columns={
        "OBCINA": "obcina",
        "VRSTA_DELA_STAVBE": "vrsta_koda",
        "PRODANA_POVRSINA": "povrsina_m2",
        "CENA": "cena_eur",
        "TRZNOST_POSLA": "trznost",
    })

    VRSTA_MAP = {
        1: "Stanovanjska hiša",
        2: "Stanovanje",
        3: "Parkirni prostor",
        4: "Garaža",
        5: "Pisarniški prostori",
        6: "Prostori za posl. s strankami",
        7: "Prostori za zdravstvo",
        8: "Trgovski/storitveni lokal",
        9: "Gostinski lokal",
        10: "Šport/kultura/izobraž.",
        11: "Industrijski prostori",
        12: "Turistični nastanitveni obj.",
        13: "Kmetijski objekt",
        14: "Tehnični/pomožni prostori",
        15: "Drugo",
    }

    df["vrsta"] = df["vrsta_koda"].map(VRSTA_MAP)

    df = df.dropna(
        subset=["cena_eur", "povrsina_m2"]
    ).copy()

    df["cena_m2"] = (
        df["cena_eur"] /
        df["povrsina_m2"]
    )

    df = df[
        (df["cena_m2"] >= 10)
        & (df["cena_m2"] <= 50000)
        & (df["povrsina_m2"] > 0)
    ]

    return df


df = load_data()

# SIDEBAR


st.sidebar.title("Filtri")

vrsta = st.sidebar.selectbox(
    "Vrsta nepremičnine",
    [
        "Stanovanje",
        "Stanovanjska hiša"
    ]
)

min_prodaj = st.sidebar.slider(
    "Minimalno število prodaj",
    1,
    100,
    10
)

# FILTRIRANJE

filtered = df[
    df["vrsta"] == vrsta
]

obcine = (
    filtered
    .groupby("obcina")
    .agg(
        mediana_cena_m2=("cena_m2", "median"),
        povprecna_cena_m2=("cena_m2", "mean"),
        stevilo_prodaj=("cena_m2", "count")
    )
    .reset_index()
)

obcine = obcine[
    obcine["stevilo_prodaj"] >= min_prodaj
]

obcine = obcine.sort_values(
    "mediana_cena_m2",
    ascending=False
)

# NASLOV

st.title("🏠 Analiza nepremičnin po občinah")

st.markdown(
    f"Analiza za: **{vrsta}**"
)

# KPI

c1, c2, c3 = st.columns(3)

c1.metric(
    "Število občin",
    len(obcine)
)

c2.metric(
    "Povprečna mediana €/m²",
    f"{obcine['mediana_cena_m2'].mean():,.0f}"
)

c3.metric(
    "Skupno prodaj",
    f"{obcine['stevilo_prodaj'].sum():,}"
)

# TOP 15

st.subheader("Top 15 občin")

top15 = obcine.head(15)

fig_top = px.bar(
    top15,
    x="obcina",
    y="mediana_cena_m2",
    hover_data=["stevilo_prodaj"],
    title=f"Top 15 občin - {vrsta}"
)

st.plotly_chart(
    fig_top,
    use_container_width=True
)

# BOTTOM 15

st.subheader("Bottom 15 občin")

bottom15 = (
    obcine
    .sort_values("mediana_cena_m2")
    .head(15)
)

fig_bottom = px.bar(
    bottom15,
    x="obcina",
    y="mediana_cena_m2",
    hover_data=["stevilo_prodaj"],
    title=f"Bottom 15 občin - {vrsta}"
)

st.plotly_chart(
    fig_bottom,
    use_container_width=True
)

st.subheader("Vse občine")

st.dataframe(
    obcine,
    use_container_width=True
)

# ZEMLJEVID

st.subheader("Zemljevid mediane cene €/m² po občinah")

with open("../obcine_map.geojson", "r", encoding="utf-8") as f:
    geo_data = json.load(f)

geo_key = "OB_UIME"

def clean(x):
    if x is None:
        return ""

    x = str(x).lower().strip()

    x = unicodedata.normalize("NFKD", x)

    x = "".join(
        c for c in x
        if not unicodedata.combining(c)
    )

    return re.sub(r"[^a-z]", "", x)

map_df = obcine.copy()

map_df["key"] = map_df["obcina"].apply(clean)

value_map = dict(
    zip(
        map_df["key"],
        map_df["mediana_cena_m2"]
    )
)

tooltip_map = dict(
    zip(
        map_df["key"],
        zip(
            map_df["mediana_cena_m2"],
            map_df["stevilo_prodaj"]
        )
    )
)

colormap = cm.LinearColormap(
    colors=["#8CB369", "#F4E285", "#F4A259", "#BC4B51"],
    vmin=map_df["mediana_cena_m2"].min(),
    vmax=map_df["mediana_cena_m2"].max()
)

def style_fn(feature):

    name = feature["properties"].get(geo_key)
    key = clean(name)

    value = value_map.get(key)

    if value is None:
        return {
            "fillColor": "#cccccc",
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.5
        }

    return {
        "fillColor": colormap(value),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.8
    }

for feat in geo_data["features"]:

    name = feat["properties"].get(geo_key)
    key = clean(name)

    if key in tooltip_map:

        cena, st = tooltip_map[key]

        feat["properties"]["tooltip"] = (
            f"{name}<br>"
            f"Mediana: {cena:,.0f} €/m²<br>"
            f"Prodaj: {st}"
        )

    else:

        feat["properties"]["tooltip"] = (
            f"{name}<br>Ni podatkov"
        )

m = folium.Map(
    location=[46.15, 14.99],
    zoom_start=8,
    tiles="cartodbpositron"
)

folium.GeoJson(
    geo_data,
    style_function=style_fn,
    tooltip=folium.GeoJsonTooltip(
        fields=["tooltip"],
        labels=False
    )
).add_to(m)

colormap.caption = f"Mediana cene ({vrsta}) €/m²"
colormap.add_to(m)

st_folium(
    m,
    width=None,
    height=650
)