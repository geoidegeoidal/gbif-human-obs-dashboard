"""
GBIF Human Observations Dashboard - Cyberpunk Edition
Single-file Streamlit app for Streamlit Cloud deployment.
"""
import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

st.set_page_config(
    page_title="GBIF HUMAN OBS // DASHBOARD",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
PRECOMPUTED = os.path.join(BASE, "dashboard", "data", "precomputed")


def load_json(name):
    p = os.path.join(PRECOMPUTED, f"{name}.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_parquet(name):
    p = os.path.join(PRECOMPUTED, f"{name}.parquet")
    if os.path.exists(p):
        return pd.read_parquet(p)
    return None


# ── Cyberpunk Palette ──────────────────────────────────────────
BG = "#06060c"
BG_CARD = "#0a0a16"
BG_SIDEBAR = "#04040a"
CYBER_CYAN = "#00e5ff"
CYBER_MAGENTA = "#ff00e5"
CYBER_GREEN = "#00ff88"
CYBER_AMBER = "#ffaa00"
CYBER_PINK = "#ff4088"
CYBER_PURPLE = "#b040ff"
CYBER_RED = "#ff3040"
CYBER_WHITE = "#e0e0f0"
CYBER_GRAY = "#7070a0"
CYBER_DIM = "#303055"
GLOW_CYAN = "0 0 12px rgba(0,229,255,0.3)"
GLOW_MAGENTA = "0 0 12px rgba(255,0,229,0.3)"
GLOW_GREEN = "0 0 12px rgba(0,255,136,0.3)"
GLOW_AMBER = "0 0 12px rgba(255,170,0,0.3)"

# ── Cyberpunk CSS ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

.stApp {{
    background: radial-gradient(ellipse at top, #0a0a20 0%, {BG} 70%);
}}

.stApp::before {{
    content: "";
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background:
        linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}}

.stApp header {{ background: transparent !important; }}
section[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR} !important;
    border-right: 1px solid {CYBER_DIM} !important;
}}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

h1, h2, h3 {{
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}}

.cyber-card {{
    background: {BG_CARD};
    border: 1px solid {CYBER_DIM};
    border-radius: 4px;
    padding: 20px 24px;
    text-align: center;
    position: relative;
    clip-path: polygon(0 10px, 10px 0, calc(100% - 10px) 0, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0 calc(100% - 10px));
}}
.cyber-card::before {{
    content: "";
    position: absolute; inset: 0;
    border: 1px solid {CYBER_CYAN};
    clip-path: polygon(0 10px, 10px 0, calc(100% - 10px) 0, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0 calc(100% - 10px));
    opacity: 0;
    transition: opacity 0.3s;
    z-index: -1;
}}
.cyber-card:hover::before {{ opacity: 0.5; }}

.cyber-kpi-value {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1.1;
}}
.cyber-kpi-label {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: {CYBER_GRAY};
    margin-top: 4px;
}}
.cyber-kpi-sub {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: {CYBER_DIM};
    margin-top: 4px;
}}

.cyber-title {{
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 2rem;
    color: {CYBER_CYAN};
    text-shadow: 0 0 15px rgba(0,229,255,0.5), 0 0 40px rgba(0,229,255,0.2);
    margin-bottom: 0;
}}

.cyber-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {CYBER_CYAN}, transparent);
    margin: 16px 0;
    opacity: 0.3;
}}

.cyber-info-box {{
    background: rgba(0,229,255,0.04);
    border-left: 3px solid {CYBER_CYAN};
    padding: 14px 18px;
    margin: 12px 0;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    color: {CYBER_WHITE};
}}

.cyber-warn-box {{
    background: rgba(255,48,64,0.06);
    border-left: 3px solid {CYBER_RED};
    padding: 14px 18px;
    margin: 12px 0;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    color: {CYBER_WHITE};
}}

.cyber-tag {{
    display: inline-block;
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    padding: 4px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: {CYBER_CYAN};
    margin: 2px;
    letter-spacing: 1px;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem;
    color: {CYBER_GRAY} !important;
    background: transparent;
    border: 1px solid {CYBER_DIM};
    padding: 8px 18px;
    letter-spacing: 2px;
}}
.stTabs [aria-selected="true"] {{
    color: {CYBER_CYAN} !important;
    background: rgba(0,229,255,0.06) !important;
    border-color: {CYBER_CYAN} !important;
    box-shadow: {GLOW_CYAN};
}}

.stSelectbox div[data-baseweb="select"] > div {{
    background: {BG_CARD} !important;
    border-color: {CYBER_DIM} !important;
    font-family: 'Share Tech Mono', monospace;
}}

.cyber-footer {{
    text-align: center;
    padding: 20px;
    margin-top: 30px;
    border-top: 1px solid {CYBER_DIM};
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: {CYBER_DIM};
    letter-spacing: 2px;
}}

.cyber-radar-box {{
    background: {BG_CARD};
    border: 1px solid {CYBER_DIM};
    padding: 12px 18px;
    border-left: 3px solid {CYBER_CYAN};
    margin: 8px 0;
    font-family: 'Rajdhani', sans-serif;
}}

.cyber-section-title {{
    font-family: 'Share Tech Mono', monospace !important;
    color: {CYBER_CYAN};
    text-shadow: 0 0 8px rgba(0,229,255,0.3);
    letter-spacing: 3px;
    font-size: 0.8rem;
    margin-bottom: 8px;
}}

/* Glitch hover effect on titles */
@keyframes glitch {{
    0% {{ text-shadow: 0 0 10px {CYBER_CYAN}; }}
    50% {{ text-shadow: 0 0 20px {CYBER_MAGENTA}, 0 0 30px {CYBER_CYAN}; }}
    100% {{ text-shadow: 0 0 10px {CYBER_CYAN}; }}
}}
.cyber-title:hover {{
    animation: glitch 0.5s ease;
}}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────
def numfmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1000:.0f}K"
    return str(int(n))


def pctfmt(n, total):
    return f"{n/total*100:.1f}%" if total > 0 else "0%"


def kpi_card(value, label, color=CYBER_CYAN, sub=""):
    sub_html = f'<div class="cyber-kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="cyber-card">
        <div class="cyber-kpi-value" style="color:{color}; text-shadow: 0 0 15px {color}40, 0 0 30px {color}20;">{value}</div>
        <div class="cyber-kpi-label">{label}</div>
        {sub_html}
    </div>
    """


def kpi_row(cards):
    cols = st.columns(len(cards))
    for col, (val, lab, col_, sub) in zip(cols, cards):
        with col:
            st.markdown(kpi_card(val, lab, col_, sub), unsafe_allow_html=True)


def cyber_divider():
    st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)


def info(text):
    st.markdown(f'<div class="cyber-info-box">{text}</div>', unsafe_allow_html=True)


def warn(text):
    st.markdown(f'<div class="cyber-warn-box">{text}</div>', unsafe_allow_html=True)


# ── Plotly theme ───────────────────────────────────────────────
pio.templates["cyber"] = go.layout.Template(layout=dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=CYBER_WHITE, family="Rajdhani, sans-serif", size=13),
    title=dict(font=dict(color=CYBER_CYAN, family="Share Tech Mono, monospace", size=18),
               x=0.02),
    xaxis=dict(gridcolor=CYBER_DIM, linecolor=CYBER_DIM, zerolinecolor=CYBER_DIM,
               title_font=dict(color=CYBER_GRAY)),
    yaxis=dict(gridcolor=CYBER_DIM, linecolor=CYBER_DIM, zerolinecolor=CYBER_DIM,
               title_font=dict(color=CYBER_GRAY)),
    legend=dict(font=dict(color=CYBER_GRAY), bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=50, b=10),
))
pio.templates.default = "cyber"


# ── Chart builders ─────────────────────────────────────────────
def chart_hbar(df, xcol, ycol, title, color_col=None, colors=None):
    fig = px.bar(df, x=xcol, y=ycol, orientation="h", title=title,
                 color=color_col, color_discrete_sequence=colors or [CYBER_CYAN])
    fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"),
                       xaxis_title="", yaxis_title="")
    fig.update_traces(hovertemplate="%{y}: <b>%{x:,.0f}</b><extra></extra>",
                       marker=dict(opacity=0.8))
    return fig


def chart_area(df, xcol, ycol, title, color=CYBER_CYAN):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[xcol], y=df[ycol],
        fill="tozeroy", mode="lines",
        line=dict(color=color, width=2),
        fillcolor=f"rgba({','.join(str(int(c)) for c in [0,229,255])},0.12)",
        hovertemplate="%{{x}}: <b>%{{y:,.0f}}</b><extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title="", yaxis_title="")
    return fig


def chart_radar(dimensions, values, title):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=dimensions,
        fill="toself", name="",
        fillcolor="rgba(0,229,255,0.12)",
        line=dict(color=CYBER_CYAN, width=2),
        hovertemplate="%{theta}: <b>%{r:.1f}/10</b><extra></extra>",
    ))
    fig.update_layout(title=title, showlegend=False,
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(visible=True, range=[0,10],
                                   gridcolor=CYBER_DIM, linecolor=CYBER_DIM,
                                   tickfont=dict(color=CYBER_GRAY)),
                   angularaxis=dict(gridcolor=CYBER_DIM, linecolor=CYBER_DIM,
                                    tickfont=dict(color=CYBER_WHITE, size=12))),
    )
    return fig


# ── Map builder ────────────────────────────────────────────────
def build_map(df):
    """Cyberpunk holographic map of human observations."""
    m = folium.Map(
        location=[-35.5, -71.5], zoom_start=5,
        tiles=None, control_scale=True,
    )
    # Cyberpunk dark basemap
    folium.TileLayer(
        tiles="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
        attr='© OSM | CartoDB',
        name="CYBER_BASE",
        control=False,
    ).add_to(m)

    # Neon heatmap
    if len(df) > 0:
        coords = df[["lat", "lon"]].values.tolist()
        HeatMap(
            coords, name="OBS_DENSITY",
            radius=10, blur=8, max_zoom=8,
            gradient={0.15: "#0a0030", 0.3: "#0000aa", 0.45: "#0044ff",
                       0.6: "#00aaff", 0.75: "#00e5ff", 0.9: "#ff00e5", 1.0: "#ff4088"},
            overlay=True,
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


# ── Load data ──────────────────────────────────────────────────
kpi = load_json("kpi") or {"total": 20801113, "human_obs": 18662018, "with_coords": 20636696, "absent": 1170113, "fossil": 7379}
phylum_human = load_json("phylum_human") or []
class_human = load_json("class_human") or []
phylum_all = load_json("phylum_all") or []
basis_dist = load_json("basis_dist") or []
year_data = load_json("year_human") or []
year_all_data = load_json("year_all") or []
month_data = load_json("month_dist") or []
prov_data = load_json("provincia_dist") or []
species_data = load_json("top_species") or []
aves_data = load_json("aves_insecta") or []
unc_data = load_json("uncertainty") or {}
comp_data = load_json("completeness") or {}
coords_df = load_parquet("coords_sample")

total = kpi.get("total", 0)
human = kpi.get("human_obs", 0)
with_coords = kpi.get("with_coords", 0)
absent = kpi.get("absent", 0)

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:20px;">
        <div style="font-size:2.4rem; filter: drop-shadow(0 0 12px #00e5ff);">▣</div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:1rem; color:#00e5ff;
                    text-shadow: 0 0 10px rgba(0,229,255,0.5); letter-spacing:3px;">
            GBIF HUMAN OBS
        </div>
        <div style="font-family:'Rajdhani',sans-serif; font-size:0.65rem; color:#7070a0;
                    letter-spacing:4px; text-transform:uppercase;">
            Chile · Animalia · @conmapas
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="cyber-divider"></div>""", unsafe_allow_html=True)

    tab = st.radio("",
        ["▸ RESUME", "▸ TAXONOMY", "▸ SPATIAL", "▸ TEMPORAL", "▸ QUALITY", "▸ BIASES"],
        label_visibility="collapsed",
    )

    st.markdown("""<div class="cyber-divider"></div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.55rem; color:{CYBER_DIM};
                line-height:2; letter-spacing:1px;">
        <div>DATA SOURCE: GBIF.ORG</div>
        <div>KINGDOM: ANIMALIA</div>
        <div>REGION: CHILE (CL)</div>
        <div>TOTAL RECORDS: {numfmt(total)}</div>
        <div>CRS: EPSG:4326</div>
    </div>
    """, unsafe_allow_html=True)


# ── Main header ────────────────────────────────────────────────
st.markdown(f'<div class="cyber-title">▸ OBSERVACIONES HUMANAS</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="font-family:'Rajdhani',sans-serif; font-size:0.7rem; color:{CYBER_GRAY};
            letter-spacing:5px; text-transform:uppercase; margin-bottom:12px;">
    {numfmt(total)} REGISTROS · REINO ANIMALIA · CHILE
</div>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 1: RESUME
# ───────────────────────────────────────────────────────────────
if tab == "▸ RESUME":
    kpi_row([
        (numfmt(total), "REGISTROS TOTALES", CYBER_AMBER, f"GBIF Animal Kingdom"),
        (numfmt(human), "HUMAN OBSERVATIONS", CYBER_CYAN, f"{pctfmt(human,total)} del total"),
        (numfmt(with_coords), "GEO-REFERENCED", CYBER_GREEN, f"{pctfmt(with_coords,total)} con lat/lon"),
        (numfmt(absent), "ABSENT FLAGGED", CYBER_RED, f"{pctfmt(absent,total)} marked absent"),
    ])
    cyber_divider()

    # Highlights
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Chordata", "89.7%", "domina human obs", delta_color="off")
    with c2:
        st.metric("Sin Class", "40.3%", "8.3M sin asignar", delta_color="off")
    with c3:
        st.metric("Sin precision", "95.0%", "sin incertidumbre", delta_color="off")
    with c4:
        st.metric("eBird/iNat", "2010", "explosion post apps", delta_color="off")

    cyber_divider()

    col_map, col_chart = st.columns([5, 4])

    with col_map:
        st.markdown('<div class="cyber-section-title">◈ HUMAN OBSERVATION DENSITY MAP</div>',
                     unsafe_allow_html=True)
        if coords_df is not None and len(coords_df) > 0:
            m = build_map(coords_df)
            st_folium(m, height=480, width="100%")
        else:
            st.warning("NO COORDINATE DATA FOUND")

    with col_chart:
        st.markdown('<div class="cyber-section-title">◈ DATA SOURCES</div>',
                     unsafe_allow_html=True)
        if basis_dist:
            df = pd.DataFrame(basis_dist)
            colors_basis = {
                "HUMAN_OBSERVATION": CYBER_CYAN,
                "MACHINE_OBSERVATION": CYBER_AMBER,
                "PRESERVED_SPECIMEN": CYBER_MAGENTA,
                "FOSSIL_SPECIMEN": CYBER_RED,
            }
            df["color"] = df["basis"].map(colors_basis).fillna(CYBER_DIM)
            fig = chart_hbar(df, "n", "basis", "BASIS OF RECORD DISTRIBUTION",
                             color_col="basis", colors=df["color"].tolist())
            fig.update_layout(height=220)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="cyber-section-title">◈ YEARLY EVOLUTION</div>',
                     unsafe_allow_html=True)
        if year_data:
            df_y = pd.DataFrame(year_data)
            fig2 = chart_area(df_y, "year", "n", "HUMAN OBSERVATIONS PER YEAR")
            fig2.update_layout(height=220)
            st.plotly_chart(fig2, use_container_width=True)

    info("**89.7%** of all GBIF Animalia records for Chile are **HUMAN_OBSERVATION**. "
         "This means citizen science platforms (eBird, iNaturalist) dominate the dataset, "
         "introducing significant taxonomic and spatial biases.")

# ───────────────────────────────────────────────────────────────
# TAB 2: TAXONOMY
# ───────────────────────────────────────────────────────────────
elif tab == "▸ TAXONOMY":
    kpi_row([
        (numfmt(next((d["n"] for d in phylum_human if d["phylum"]=="Chordata"), 0)),
         "CHORDATA (HUMAN)", CYBER_CYAN,
         pctfmt(next((d["n"] for d in phylum_human if d["phylum"]=="Chordata"), 0),
                sum(d["n"] for d in phylum_human))),
        (numfmt(next((d["n"] for d in phylum_human if d["phylum"]=="Arthropoda"), 0)),
         "ARTHROPODA (HUMAN)", CYBER_AMBER,
         pctfmt(next((d["n"] for d in phylum_human if d["phylum"]=="Arthropoda"), 0),
                sum(d["n"] for d in phylum_human))),
        (numfmt(next((d["n"] for d in phylum_human if d["phylum"]=="Mollusca"), 0)),
         "MOLLUSCA (HUMAN)", CYBER_MAGENTA,
         pctfmt(next((d["n"] for d in phylum_human if d["phylum"]=="Mollusca"), 0),
                sum(d["n"] for d in phylum_human))),
        (f"{len(phylum_human)}", "PHYLA DETECTED", CYBER_PURPLE, "in human observations"),
    ])
    cyber_divider()

    c1, c2 = st.columns(2)
    with c1:
        if phylum_human:
            df = pd.DataFrame([d for d in phylum_human if d["phylum"]!="Sin dato"][:10])
            phylum_colors = {"Chordata": CYBER_CYAN, "Arthropoda": CYBER_AMBER,
                             "Mollusca": CYBER_MAGENTA, "Echinodermata": CYBER_PINK,
                             "Cnidaria": CYBER_PURPLE, "Annelida": CYBER_GREEN}
            df["c"] = df["phylum"].map(phylum_colors).fillna(CYBER_DIM)
            fig = chart_hbar(df, "n", "phylum", "PHYLUM IN HUMAN OBSERVATIONS",
                             color_col="phylum", colors=df["c"].tolist())
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if class_human:
            df = pd.DataFrame([d for d in class_human if d["class"]!="Sin dato"][:12])
            fig2 = chart_hbar(df, "n", "class", "TOP CLASSES IN HUMAN OBSERVATIONS",
                              color_col="phylum")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="cyber-section-title">◈ MOST OBSERVED SPECIES</div>',
                 unsafe_allow_html=True)
    if species_data:
        df = pd.DataFrame(species_data[:15])
        fig3 = chart_hbar(df, "n", "species", "HUMAN OBSERVATION · TOP 15 SPECIES",
                          color_col="class")
        st.plotly_chart(fig3, use_container_width=True)

    warn("**Aves outnumber Insecta 115:1 in human observations.** "
         "Despite insects being the most diverse animal group on Earth, birdwatchers "
         "using eBird dominate the dataset. Museum collections (PRESERVED_SPECIMEN) "
         "show the opposite pattern, with insects comprising the majority.")

# ───────────────────────────────────────────────────────────────
# TAB 3: SPATIAL
# ───────────────────────────────────────────────────────────────
elif tab == "▸ SPATIAL":
    st.markdown('<div class="cyber-section-title">◈ HUMAN OBSERVATION DENSITY · CHILE</div>',
                 unsafe_allow_html=True)

    if coords_df is not None and len(coords_df) > 0:
        m = build_map(coords_df)
        st_folium(m, height=550, width="100%")

    info("Observations concentrate in urban and coastal areas (Santiago, Valparaiso, Concepcion). "
         "Patagonia, the Altiplano, and Andean regions show significant sampling gaps.")

    if prov_data:
        df = pd.DataFrame(prov_data[:15])
        df = df[~df["provincia"].str.match(r"^\d+$", na=False)]
        fig = chart_hbar(df, "n", "provincia", "TOP PROVINCES · HUMAN OBSERVATIONS")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Top 5 Regions", "~45%", "concentrate observations", delta_color="off")
    with c2:
        st.metric("No Province Data", "7.5M", "36% missing stateProvince", delta_color="off")
    with c3:
        st.metric("Urban Bias", "HIGH", "Santiago > Patagonia", delta_color="off")

# ───────────────────────────────────────────────────────────────
# TAB 4: TEMPORAL
# ───────────────────────────────────────────────────────────────
elif tab == "▸ TEMPORAL":
    if year_data:
        df = pd.DataFrame(year_data)
        peak = df.loc[df["n"].idxmax()]
        recent = df[df["year"] >= 2020]["n"].sum()
        all_sum = df["n"].sum()
        kpi_row([
            (f"{int(peak['year'])}", "PEAK YEAR", CYBER_CYAN, f"{peak['n']:,.0f} records"),
            (numfmt(recent), "2020-2024 TOTAL", CYBER_AMBER, pctfmt(recent, all_sum)),
            (numfmt(all_sum), "1950+ TOTAL", CYBER_GREEN, "Human Observations"),
            ("x370", "GROWTH 1970-2023", CYBER_MAGENTA, "explosion post-eBird"),
        ])

    cyber_divider()

    if year_data:
        fig = chart_area(pd.DataFrame(year_data), "year", "n",
                         "HUMAN OBSERVATIONS PER YEAR (1950-2025)")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    info("**Post-2010 explosion.** eBird (2002) and iNaturalist (2008) revolutionized citizen science. "
         "Between 2020-2024, 38% of all human observations were recorded. "
         "COVID-19 lockdowns increased backyard birding activity.")

    if month_data:
        months = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",
                  7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}
        df = pd.DataFrame(month_data)
        df["mes"] = df["month"].map(months)
        fig2 = px.bar(df, x="mes", y="n", title="SEASONALITY · HUMAN OBSERVATIONS BY MONTH",
                       color_discrete_sequence=[CYBER_CYAN])
        fig2.update_traces(hovertemplate="%{x}: <b>%{y:,.0f}</b><extra></extra>",
                            marker=dict(opacity=0.7))
        fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="cyber-section-title">◈ KEY EVENTS</div>',
                 unsafe_allow_html=True)
    events = [
        ("2002", "eBird launch", "Bird observation goes digital"),
        ("2008", "iNaturalist launch", "All-taxa citizen science platform"),
        ("2010", ">800K records/year", "Citizen platforms reach maturity"),
        ("2014", "GBIF Chile node", "National data integration begins"),
        ("2020", "COVID-19", "Backyard birding surge during lockdowns"),
        ("2022", "1.8M peak", "All-time annual record for Chile"),
    ]
    for yr, title, desc in events:
        st.markdown(f"""
        <div style="display:flex; align-items:baseline; gap:16px; margin:6px 0;
                    font-family:'Share Tech Mono',monospace;">
            <span style="color:{CYBER_CYAN}; min-width:50px; font-weight:bold;">{yr}</span>
            <span style="color:{CYBER_WHITE}; font-weight:bold;">{title}</span>
            <span style="color:{CYBER_GRAY}; font-size:0.75rem;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 5: QUALITY
# ───────────────────────────────────────────────────────────────
elif tab == "▸ QUALITY":
    if comp_data:
        tot = comp_data.get("total", 1)
        kpi_row([
            (pctfmt(comp_data.get("species_ok",0), tot), "WITH SPECIES", CYBER_GREEN,
             numfmt(comp_data.get("species_ok",0))),
            (pctfmt(comp_data.get("class_ok",0), tot), "WITH CLASS", CYBER_AMBER,
             numfmt(comp_data.get("class_ok",0))),
            (pctfmt(comp_data.get("phylum_ok",0), tot), "WITH PHYLUM", CYBER_CYAN,
             numfmt(comp_data.get("phylum_ok",0))),
            ("40.3%", "MISSING CLASS", CYBER_RED, "8.3M unclassified"),
        ])

    cyber_divider()

    # Completeness chart
    if comp_data:
        tot = comp_data.get("total", 1)
        fields = [
            ("PHYLUM", comp_data.get("phylum_ok", 0)),
            ("CLASS", comp_data.get("class_ok", 0)),
            ("ORDER", comp_data.get("order_ok", 0)),
            ("FAMILY", comp_data.get("family_ok", 0)),
            ("GENUS", comp_data.get("genus_ok", 0)),
            ("SPECIES", comp_data.get("species_ok", 0)),
            ("DATE", comp_data.get("date_ok", 0)),
        ]
        df_c = pd.DataFrame(fields, columns=["FIELD", "COMPLETE"])
        df_c["%"] = df_c["COMPLETE"] / tot * 100
        df_c["MISSING%"] = 100 - df_c["%"]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df_c["FIELD"], x=df_c["%"], name="COMPLETE",
                              orientation="h", marker=dict(color=CYBER_GREEN, opacity=0.6)))
        fig.add_trace(go.Bar(y=df_c["FIELD"], x=df_c["MISSING%"], name="MISSING",
                              orientation="h", marker=dict(color=CYBER_RED, opacity=0.4)))
        fig.update_layout(title="TAXONOMIC FIELD COMPLETENESS", barmode="stack",
                           bargap=0.3, xaxis_title="%", yaxis_title="",
                           showlegend=True, height=300)
        st.plotly_chart(fig, use_container_width=True)

    warn("**40.3% of records lack Class assignment (8.3M).** These records are virtually "
         "unusable for taxonomic analysis without additional processing.")

    # Uncertainty
    if unc_data:
        unc_tot = unc_data.get("total", 1)
        sin = unc_data.get("sin_dato", 0)
        st.markdown('<div class="cyber-section-title">◈ COORDINATE UNCERTAINTY</div>',
                     unsafe_allow_html=True)
        kpi_row([
            (pctfmt(sin, unc_tot), "NO UNCERTAINTY DATA", CYBER_RED, f"{numfmt(sin)} records"),
            (f"{unc_data.get('mediana_m',0):,.0f}m", "MEDIAN (WHEN REPORTED)", CYBER_AMBER),
            (f"{unc_data.get('promedio_m',0):,.0f}m", "MEAN (WHEN REPORTED)", CYBER_CYAN),
            ("7,945km", "MAX UNCERTAINTY", CYBER_MAGENTA, "FOSSIL_SPECIMEN"),
        ])

        cats = [("NO DATA", sin, CYBER_RED), ("<=10m", unc_data.get("hasta_10m",0), CYBER_GREEN),
                ("10-100m", unc_data.get("de_10_100m",0), CYBER_GREEN),
                ("100m-1km", unc_data.get("de_100_1000m",0), CYBER_CYAN),
                ("1-10km", unc_data.get("de_1_10km",0), CYBER_AMBER),
                ("10-100km", unc_data.get("de_10_100km",0), CYBER_MAGENTA),
                (">100km", unc_data.get("mas_100km",0), CYBER_RED)]
        df_u = pd.DataFrame(cats, columns=["CATEGORY", "N", "COLOR"])
        df_u["%"] = df_u["N"] / unc_tot * 100
        fig_u = px.bar(df_u, x="N", y="CATEGORY", orientation="h", text="%",
                        title="UNCERTAINTY DISTRIBUTION", color="COLOR",
                        color_discrete_map="identity")
        fig_u.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                             hovertemplate="%{y}: %{x:,.0f} (%{text:.1f}%)<extra></extra>")
        fig_u.update_layout(showlegend=False, yaxis=dict(autorange="reversed"),
                             xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_u, use_container_width=True)

    warn("**95% of records do NOT report coordinateUncertaintyInMeters.** "
         "Without this field, it's impossible to assess geospatial precision. "
         "Always filter or assume a default uncertainty for serious analysis.")

    # Checklist
    st.markdown('<div class="cyber-section-title">◈ DATA QUALITY CHECKLIST</div>',
                 unsafe_allow_html=True)
    checks = [
        ("01", CYBER_GREEN, "Filter occurrenceStatus = PRESENT", "Excludes 1.17M ABSENT records"),
        ("02", CYBER_GREEN, "Exclude FOSSIL_SPECIMEN", "7,379 fossils with ~1,949km uncertainty"),
        ("03", CYBER_GREEN, "Check coordinateUncertaintyInMeters", "95% of records missing this field"),
        ("04", CYBER_AMBER, "Separate by basisOfRecord", "Human vs Machine vs Museum: different behaviors"),
        ("05", CYBER_AMBER, "Verify taxonomic identification", "40.3% without Class assignment"),
    ]
    for num, color, check, detail in checks:
        st.markdown(f"""
        <div style="display:flex; gap:12px; margin:8px 0; font-family:'Rajdhani',sans-serif;">
            <span style="color:{color}; font-weight:bold; min-width:28px;">[{num}]</span>
            <span style="color:{CYBER_WHITE}; flex:1;">{check}</span>
            <span style="color:{CYBER_GRAY}; font-size:0.75rem;">{detail}</span>
        </div>
        """, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 6: BIASES
# ───────────────────────────────────────────────────────────────
elif tab == "▸ BIASES":
    radar_dims = ["TAXONOMIC\n(Birds >> Insects)", "SPATIAL\n(Urban >> Rural)",
                  "TEMPORAL\n(Post-2010)", "ACCESSIBILITY\n(Near Roads)",
                  "DETECTABILITY\n(Large >> Small)", "PLATFORM\n(eBird/iNat Bias)",
                  "QUALITY\n(95% No Precision)"]
    radar_vals = [9.0, 8.5, 7.0, 8.0, 7.5, 8.5, 9.0]
    fig_r = chart_radar(radar_dims, radar_vals, "BIAS RADAR · 0=NO BIAS / 10=EXTREME BIAS")
    st.plotly_chart(fig_r, use_container_width=True)

    cyber_divider()

    if basis_dist:
        df_b = pd.DataFrame(basis_dist)
        colors_b = {"HUMAN_OBSERVATION": CYBER_CYAN, "MACHINE_OBSERVATION": CYBER_AMBER,
                     "PRESERVED_SPECIMEN": CYBER_MAGENTA, "FOSSIL_SPECIMEN": CYBER_RED}
        df_b["c"] = df_b["basis"].map(colors_b).fillna(CYBER_DIM)
        fig_b = chart_hbar(df_b, "n", "basis", "DATA SOURCE COMPARISON",
                           color_col="basis", colors=df_b["c"].tolist())
        st.plotly_chart(fig_b, use_container_width=True)

    coll, colr = st.columns(2)
    with coll:
        st.markdown(f"""
        <div class="cyber-radar-box" style="border-color:{CYBER_CYAN};">
            <div style="font-family:'Share Tech Mono',monospace; color:{CYBER_CYAN};
                        font-size:0.8rem; margin-bottom:6px;">■ HUMAN OBSERVATION</div>
            <div style="color:{CYBER_GRAY}; font-size:0.75rem;">
                89.7% of data · Citizen science<br>
                eBird + iNaturalist dominant<br>
                Bias toward large/diurnal vertebrates<br>
                Urban and coastal concentration<br>
                Post-2010 data explosion
            </div>
        </div>
        """, unsafe_allow_html=True)
    with colr:
        st.markdown(f"""
        <div class="cyber-radar-box" style="border-color:{CYBER_MAGENTA};">
            <div style="font-family:'Share Tech Mono',monospace; color:{CYBER_MAGENTA};
                        font-size:0.8rem; margin-bottom:6px;">■ PRESERVED SPECIMEN</div>
            <div style="color:{CYBER_GRAY}; font-size:0.75rem;">
                2.0% of data · Museum collections<br>
                Better invertebrate coverage<br>
                Rigorous taxonomic identification<br>
                Historical distribution (wider)<br>
                Less recent spatial bias
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="cyber-section-title">◈ INTERPRETATION GUIDE</div>',
                 unsafe_allow_html=True)

    biases = [
        (CYBER_CYAN, "PLATFORM BIAS",
         "eBird accounts for >40% of human observations. The dataset is dominated by "
         "birdwatchers, not representative biodiversity sampling."),
        (CYBER_AMBER, "ACCESSIBILITY BIAS",
         "Observations cluster near roads, cities, and tourist trails. Remote areas "
         "(inner Patagonia, Altiplano, Andes) are severely under-sampled."),
        (CYBER_MAGENTA, "DETECTABILITY BIAS",
         "Large, diurnal, colorful, or loud animals are overrepresented. Small "
         "invertebrates, nocturnal, and cryptic species are underrepresented."),
        (CYBER_RED, "COMPLETENESS BIAS",
         "95% don't report coordinate precision. 40.3% lack Class assignment. "
         "1.17M are ABSENT records confused with presence."),
    ]
    for color, title, txt in biases:
        st.markdown(f"""
        <div style="border-left:3px solid {color}; padding:8px 16px; margin:10px 0;">
            <div style="font-family:'Share Tech Mono',monospace; color:{color};
                        font-size:0.8rem; margin-bottom:4px;">▸ {title}</div>
            <div style="color:{CYBER_GRAY}; font-size:0.8rem;">{txt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center; margin-top:20px; padding:16px;
                border:1px solid {CYBER_CYAN}; border-left:0; border-right:0;">
        <span style="font-family:'Share Tech Mono',monospace; color:{CYBER_WHITE};
                     font-size:1rem; letter-spacing:3px;">
            "DATA WITHOUT CONTEXT IS A MAP THAT LIES"
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="cyber-footer">
    ▸ GBIF.ORG · REGNUM ANIMALIA · CHILE (CL) · @CONMAPAS · {total:,.0f} RECORDS ◂
</div>
""", unsafe_allow_html=True)
