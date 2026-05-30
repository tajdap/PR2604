import streamlit as st

st.set_page_config(
    page_title="Demografija Slovenije",
    page_icon="🇸🇮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #1e1e2e;
    }
    [data-testid="stSidebar"] * {
        color: #cfd1d3 !important;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #BC4B51;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #5B8E7D;
        margin-bottom: 2rem;
    }
    .card {
        background: #f9f9f9;
        border-left: 4px solid #BC4B51;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🇸🇮 Demografija Slovenije</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interaktivna analiza rojstev, rodnosti in plač po občinah</div>', unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📚 Izobrazba matere</h3>
        <p>Analiza prvih rojstev glede na stopnjo izobrazbe matere (2010–2024)</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>👩 Starost matere</h3>
        <p>Trendi prvih rojstev po starostnih skupinah mater skozi leta</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h3>🏘️ Tip okolja</h3>
        <p>Primerjava rodnosti med mestnim in podeželskim okoljem po obdobjih</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="card">
        <h3>💰 Plača & rojstva</h3>
        <p>Zemljevid bruto plač in primerjava z rodnostjo po občinah</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📂 Navigacija")
st.info("Izberi stran v **stranski vrstici** (levo) za ogled posamezne analize.")

st.markdown("""
<br>
<small style='color:#aaa;'>Vir podatkov: SURS · Vizualizacija: Streamlit + Plotly</small>
""", unsafe_allow_html=True)
