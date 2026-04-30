"""
Estilos CSS inyectados en Streamlit.
Tema oscuro consistente con la paleta del carrusel @conmapas.
"""

import streamlit as st
from dashboard.config import BG, AMBER, CYAN, MAGENTA, GREEN, RED, WHITE, GRAY, GRAY_DIM


CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    /* Override Streamlit defaults */
    .stApp {{
        background-color: {BG};
    }}

    .stApp header[data-testid="stHeader"] {{
        background-color: {BG};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: #0a0f15;
        border-right: 1px solid {GRAY_DIM};
    }}
    section[data-testid="stSidebar"] * {{
        color: {GRAY} !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {WHITE} !important;
    }}

    /* Main content */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    /* Hide default streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Headers */
    h1, h2, h3 {{
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
        color: {WHITE} !important;
    }}

    /* KPI Cards */
    .kpi-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    .kpi-card {{
        flex: 1;
        min-width: 180px;
        background: linear-gradient(135deg, #111827, #0f172a);
        border: 1px solid {GRAY_DIM};
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        transition: border-color 0.3s;
    }}
    .kpi-card:hover {{
        border-color: {CYAN};
    }}
    .kpi-card .kpi-value {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 0.3rem;
    }}
    .kpi-card .kpi-label {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 0.8rem;
        color: {GRAY};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .kpi-card .kpi-sub {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 0.7rem;
        color: {GRAY_DIM};
        margin-top: 0.2rem;
    }}

    /* Info box */
    .info-box {{
        background: rgba(34, 211, 238, 0.06);
        border: 1px solid rgba(34, 211, 238, 0.2);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: {GRAY};
        font-size: 0.85rem;
    }}
    .info-box strong {{
        color: {CYAN};
    }}

    .warning-box {{
        background: rgba(248, 113, 113, 0.06);
        border: 1px solid rgba(248, 113, 113, 0.2);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: {GRAY};
        font-size: 0.85rem;
    }}
    .warning-box strong {{
        color: {RED};
    }}

    /* Footer */
    .dashboard-footer {{
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid {GRAY_DIM};
        color: {GRAY_DIM};
        font-size: 0.7rem;
    }}

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: {BG};
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: {GRAY} !important;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.2rem;
    }}
    .stTabs [aria-selected="true"] {{
        color: {CYAN} !important;
        background-color: rgba(34, 211, 238, 0.08) !important;
        border-bottom: 2px solid {CYAN} !important;
    }}

    /* DataFrame table */
    .stDataFrame {{
        background-color: #111827;
        border: 1px solid {GRAY_DIM};
        border-radius: 8px;
    }}

    /* Select boxes and inputs */
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiselect div[data-baseweb="select"] > div {{
        background-color: #111827;
        border-color: {GRAY_DIM};
        color: {WHITE};
    }}
</style>
"""


def inject_css():
    """Inject CSS into the Streamlit app."""
    st.markdown(CSS, unsafe_allow_html=True)


def footer():
    """Render dashboard footer."""
    st.markdown(
        f'<div class="dashboard-footer">'
        f'GBIF.org · Reino Animalia · Chile (CL) · @conmapas · {{{{ }} }}'
        f'</div>',
        unsafe_allow_html=True,
    )


def kpi_card(value, label, color=AMBER, subtitle=None):
    """Render a single KPI card as HTML."""
    sub_html = f'<div class="kpi-sub">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-label">{label}</div>
        {sub_html}
    </div>
    """


def kpi_row(cards):
    """Render a row of KPI cards."""
    st.markdown(
        '<div class="kpi-container">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def info_box(text):
    """Render an info box."""
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)


def warning_box(text):
    """Render a warning box."""
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)
