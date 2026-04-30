"""
GBIF Human Observations Dashboard - Cyberpunk Edition v2
Single-file Streamlit app · Español · Hexbin cyberpunk map
"""
import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import plotly.figure_factory as ff

st.set_page_config(
    page_title="GBIF HUMAN OBS // DASHBOARD",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE = os.getcwd()
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

# ── Cyberpunk CSS ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

.stApp {{
    background: radial-gradient(ellipse at top, #0a0a20 0%, {BG} 70%);
    position: relative;
}}

.stApp::before {{
    content: "";
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background:
        linear-gradient(rgba(0,229,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,0.025) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}}

.stApp::after {{
    content: "";
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,229,255,0.012) 2px,
        rgba(0,229,255,0.012) 4px
    );
    pointer-events: none; z-index: 1;
    animation: scanline 8s linear infinite;
}}
@keyframes scanline {{
    0% {{ transform: translateY(0); }}
    100% {{ transform: translateY(4px); }}
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
    background: rgba(10, 10, 22, 0.45);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid {CYBER_DIM};
    border-radius: 4px;
    padding: 20px 24px;
    text-align: center;
    position: relative;
    clip-path: polygon(0 10px, 10px 0, calc(100% - 10px) 0, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0 calc(100% - 10px));
    transition: border-color 0.3s, box-shadow 0.3s;
    overflow: hidden;
}}
.cyber-card::after {{
    content: "";
    position: absolute; inset: 0;
    border: 1px solid transparent;
    clip-path: polygon(0 10px, 10px 0, calc(100% - 10px) 0, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0 calc(100% - 10px));
    pointer-events: none;
    animation: pulse_glow 3s ease-in-out infinite;
}}
@keyframes pulse_glow {{
    0%, 100% {{
        border-color: rgba(0,229,255,0.05);
        box-shadow: 0 0 8px rgba(0,229,255,0.03), inset 0 0 8px rgba(0,229,255,0.01);
    }}
    50% {{
        border-color: rgba(0,229,255,0.15);
        box-shadow: 0 0 16px rgba(0,229,255,0.08), inset 0 0 16px rgba(0,229,255,0.03);
    }}
}}
.cyber-card:hover {{
    border-color: {CYBER_CYAN};
    box-shadow: 0 0 20px rgba(0,229,255,0.2), inset 0 0 20px rgba(0,229,255,0.05);
}}

.cyber-kpi-value {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.3rem;
    font-weight: 700;
    line-height: 1.1;
}}
.cyber-kpi-label {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 5px;
    color: rgba(224, 224, 240, 0.6);
    margin-top: 6px;
}}
.cyber-kpi-sub {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: rgba(224, 224, 240, 0.35);
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

.cyber-section-title {{
    font-family: 'Share Tech Mono', monospace !important;
    color: {CYBER_CYAN};
    text-shadow: 0 0 8px rgba(0,229,255,0.3);
    letter-spacing: 4px;
    font-size: 0.75rem;
    margin-bottom: 8px;
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
    box-shadow: 0 0 12px rgba(0,229,255,0.3);
}}

.cyber-footer {{
    text-align: center;
    padding: 20px;
    margin-top: 30px;
    border-top: 1px solid {CYBER_DIM};
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: {CYBER_DIM};
    letter-spacing: 3px;
}}

.cyber-radar-box {{
    background: rgba(10, 10, 22, 0.45);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid {CYBER_DIM};
    padding: 12px 18px;
    margin: 8px 0;
    font-family: 'Rajdhani', sans-serif;
}}

@keyframes glitch {{
    0% {{ text-shadow: 0 0 10px {CYBER_CYAN}; }}
    50% {{ text-shadow: 0 0 20px {CYBER_MAGENTA}, 0 0 30px {CYBER_CYAN}; }}
    100% {{ text-shadow: 0 0 10px {CYBER_CYAN}; }}
}}
.cyber-title:hover {{
    animation: glitch 0.5s ease;
}}

.cyber-blink {{
    animation: blink 2s infinite;
}}
@keyframes blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.3; }}
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
        fillcolor=f"rgba(0,229,255,0.12)",
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


def chart_hexbin(df, title):
    """Hexbin density chart usando plotly (alternativa al heatmap)."""
    fig = ff.create_hexbin_map(
        data_frame=df, lat="lat", lon="lon",
        nx_hexagon=30, opacity=0.5, min_count=1,
        labels={"color": "Obs"},
        color_continuous_scale=[
            [0.0, "#06060c"], [0.15, "#0a0030"], [0.3, "#0000aa"],
            [0.5, "#0044ff"], [0.65, "#00aaff"], [0.8, "#00e5ff"],
            [0.9, "#ff00e5"], [1.0, "#ff4088"],
        ],
        map_style="carto-darkmatter",
        zoom=4, center={"lat": -35.5, "lon": -71.5},
        height=550,
    )
    fig.update_layout(title=title, margin=dict(l=0, r=0, t=50, b=0),
                       coloraxis_showscale=False)
    return fig


# ── Map builder (cyberpunk cluster + hexbin) ───────────────────
def build_cluster_map(df, mode="cluster"):
    """Mapa cyberpunk con clusters neon o hexbin interactivo."""
    m = folium.Map(
        location=[-35.5, -71.5], zoom_start=5,
        tiles=None, control_scale=True,
    )
    folium.TileLayer(
        tiles="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
        attr='© OSM | CartoDB',
        name="CYBER_BASE",
        control=False,
    ).add_to(m)

    if len(df) == 0:
        return m

    if mode == "cluster":
        sample = df.sample(min(len(df), 8000)) if len(df) > 8000 else df
        marker_cluster = MarkerCluster(
            name="CLUSTERS NEON",
            icon_create_function="""
                function(cluster) {
                    var count = cluster.getChildCount();
                    var size = count < 100 ? 30 : count < 500 ? 40 : count < 2000 ? 50 : 60;
                    var color = count < 100 ? '#00e5ff' : count < 500 ? '#00ff88' : count < 2000 ? '#ffaa00' : '#ff00e5';
                    return L.divIcon({
                        html: '<div style="background:' + color + '20; border:2px solid ' + color +
                              '; border-radius:50%; width:' + size + 'px; height:' + size +
                              'px; display:flex; align-items:center; justify-content:center;' +
                              ' font-family:monospace; font-size:11px; color:' + color +
                              '; text-shadow:0 0 8px ' + color + '; box-shadow:0 0 15px ' +
                              color + '40, inset 0 0 10px ' + color + '20;">' + count + '</div>',
                        className: '', iconSize: L.point(size, size)
                    });
                }
            """,
        ).add_to(m)
        for _, row in sample.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=2,
                color="#00e5ff",
                fill=True,
                fill_opacity=0.6,
            ).add_to(marker_cluster)

    elif mode == "hexbin":
        folium.plugins.HeatMap(
            data=df[["lat", "lon"]].values.tolist(),
            name="HEXBIN DENSITY",
            radius=15, blur=10, max_zoom=8,
            gradient={0.1: "#0a0030", 0.25: "#0000aa", 0.4: "#0044ff",
                       0.55: "#00aaff", 0.7: "#00e5ff", 0.85: "#ff00e5", 1.0: "#ff4088"},
            overlay=True,
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


# ── Load all data ──────────────────────────────────────────────
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

    cyber_divider()

    tab = st.radio("",
        ["▸ RESUMEN", "▸ TAXONOMIA", "▸ ESPACIAL", "▸ TEMPORAL", "▸ CALIDAD", "▸ SESGOS"],
        label_visibility="collapsed",
    )

    cyber_divider()

    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.55rem; color:{CYBER_DIM};
                line-height:2; letter-spacing:1px;">
        <div>FUENTE: GBIF.ORG</div>
        <div>REINO: ANIMALIA</div>
        <div>REGIÓN: CHILE (CL)</div>
        <div>TOTAL: {numfmt(total)} REG</div>
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

# ═══════════════════════════════════════════════════════════════
# TAB 1: RESUMEN
# ═══════════════════════════════════════════════════════════════
if tab == "▸ RESUMEN":
    kpi_row([
        (numfmt(total), "REGISTROS TOTALES", CYBER_AMBER, "GBIF Reino Animalia"),
        (numfmt(human), "OBSERVACIONES HUMANAS", CYBER_CYAN, f"{pctfmt(human,total)} del total"),
        (numfmt(with_coords), "GEORREFERENCIADOS", CYBER_GREEN, f"{pctfmt(with_coords,total)} con lat/lon"),
        (numfmt(absent), "REGISTROS ABSENT", CYBER_RED, f"{pctfmt(absent,total)} marcados ausentes"),
    ])
    cyber_divider()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Chordata", "89.7%", "domina obs. humanas", delta_color="off")
    with c2:
        st.metric("Sin Clase", "40.3%", "8.3M sin asignar", delta_color="off")
    with c3:
        st.metric("Sin Precisión", "95.0%", "sin incertidumbre", delta_color="off")
    with c4:
        st.metric("eBird/iNat", "2010", "explosión post apps", delta_color="off")

    cyber_divider()

    st.markdown('<div class="cyber-section-title">◈ MAPA DE DENSIDAD · OBSERVACIONES HUMANAS</div>',
                 unsafe_allow_html=True)

    map_mode = st.radio(
        "Visualización:",
        ["Hexbin Interactivo (Plotly)", "Clusters Neon (Folium)", "Densidad Holográfica (Folium)"],
        horizontal=True, label_visibility="collapsed",
    )

    col_map, col_chart = st.columns([5, 4])

    with col_map:
        if coords_df is not None and len(coords_df) > 0:
            try:
                with st.spinner("Cargando mapa interactivo..."):
                    if "Plotly" in map_mode:
                        fig_hx = chart_hexbin(coords_df, "DENSIDAD HEXBIN · OBSERVACIONES HUMANAS")
                        st.plotly_chart(fig_hx, use_container_width=True)
                    else:
                        mode = "cluster" if "Clusters" in map_mode else "hexbin"
                        m = build_cluster_map(coords_df, mode=mode)
                        st_folium(m, height=500, width="100%")
            except Exception as e:
                warn("Error al renderizar la capa geográfica.")
        else:
            st.warning("NO SE ENCONTRARON COORDENADAS DE MUESTRA")

    with col_chart:
        st.markdown('<div class="cyber-section-title">◈ FUENTE DE LOS DATOS</div>',
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
            fig = chart_hbar(df, "n", "basis", "DISTRIBUCIÓN POR BASIS OF RECORD",
                             color_col="basis", colors=df["color"].tolist())
            fig.update_layout(height=220)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="cyber-section-title">◈ EVOLUCIÓN ANUAL</div>',
                     unsafe_allow_html=True)
        if year_data:
            df_y = pd.DataFrame(year_data)
            fig2 = chart_area(df_y, "year", "n", "OBSERVACIONES HUMANAS POR AÑO")
            fig2.update_layout(height=220)
            st.plotly_chart(fig2, use_container_width=True)

    info("El **89.7%** de los registros GBIF Animalia para Chile son **HUMAN_OBSERVATION**. "
         "Esto significa que la ciencia ciudadana (eBird, iNaturalist) domina el dataset, "
         "introduciendo sesgos taxonómicos y espaciales significativos.")

# ═══════════════════════════════════════════════════════════════
# TAB 2: TAXONOMIA
# ═══════════════════════════════════════════════════════════════
elif tab == "▸ TAXONOMIA":
    st.markdown('<div class="cyber-section-title">◈ ¿QUÉ SE OBSERVA? · DISTRIBUCIÓN TAXONÓMICA</div>',
                 unsafe_allow_html=True)

    chordata_n = next((d["n"] for d in phylum_human if d["phylum"]=="Chordata"), 0)
    arthropoda_n = next((d["n"] for d in phylum_human if d["phylum"]=="Arthropoda"), 0)
    mollusca_n = next((d["n"] for d in phylum_human if d["phylum"]=="Mollusca"), 0)
    total_human_phylum = sum(d["n"] for d in phylum_human)

    kpi_row([
        (numfmt(chordata_n), "CHORDATA", CYBER_CYAN,
         pctfmt(chordata_n, total_human_phylum)),
        (numfmt(arthropoda_n), "ARTHROPODA", CYBER_AMBER,
         pctfmt(arthropoda_n, total_human_phylum)),
        (numfmt(mollusca_n), "MOLLUSCA", CYBER_MAGENTA,
         pctfmt(mollusca_n, total_human_phylum)),
        (str(len(phylum_human)), "PHYLA DETECTADOS", CYBER_PURPLE, "en obs. humanas"),
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
            fig = chart_hbar(df, "n", "phylum", "PHYLUM EN OBSERVACIONES HUMANAS",
                             color_col="phylum", colors=df["c"].tolist())
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if class_human:
            df = pd.DataFrame([d for d in class_human if d["class"]!="Sin dato"][:12])
            fig2 = chart_hbar(df, "n", "class", "CLASES EN OBSERVACIONES HUMANAS",
                              color_col="phylum")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="cyber-section-title">◈ ESPECIES MÁS OBSERVADAS</div>',
                 unsafe_allow_html=True)
    if species_data:
        df = pd.DataFrame(species_data[:15])
        fig3 = chart_hbar(df, "n", "species", "TOP 15 ESPECIES · OBSERVACIÓN HUMANA",
                          color_col="class")
        st.plotly_chart(fig3, use_container_width=True)

    aves_val = next((d["n"] for d in aves_data if d["class"]=="Aves"), 0)
    insecta_val = next((d["n"] for d in aves_data if d["class"]=="Insecta"), 0)
    ratio = aves_val / insecta_val if insecta_val > 0 else 0

    warn(f"**Hay {ratio:.0f} aves por cada insecto registrado.** "
         f"A pesar de que los insectos son el grupo animal más diverso del planeta, "
         f"los observadores de aves en eBird dominan abrumadoramente el dataset. "
         f"En colecciones de museo (PRESERVED_SPECIMEN) el patrón se invierte: "
         f"los insectos son mayoría (249K especímenes).")

# ═══════════════════════════════════════════════════════════════
# TAB 3: ESPACIAL
# ═══════════════════════════════════════════════════════════════
elif tab == "▸ ESPACIAL":
    st.markdown('<div class="cyber-section-title">◈ ¿DÓNDE SE OBSERVA? · CONCENTRACIÓN GEOGRÁFICA</div>',
                 unsafe_allow_html=True)

    if coords_df is not None and len(coords_df) > 0:
        map_mode2 = st.radio(
            "Visualización:",
            ["Hexbin Interactivo (Plotly)", "Clusters Neon (Folium)", "Densidad Holográfica (Folium)"],
            horizontal=True, label_visibility="collapsed",
        )
        try:
            with st.spinner("Cargando mapa interactivo..."):
                if "Plotly" in map_mode2:
                    fig_hx = chart_hexbin(coords_df, "DENSIDAD HEXBIN · OBSERVACIONES HUMANAS EN CHILE")
                    st.plotly_chart(fig_hx, use_container_width=True)
                else:
                    mode = "cluster" if "Clusters" in map_mode2 else "hexbin"
                    m = build_cluster_map(coords_df, mode=mode)
                    st_folium(m, height=600, width="100%")
        except Exception as e:
            warn("Error al renderizar la capa geográfica.")

    info("Las observaciones humanas se concentran en zonas urbanas y costeras "
         "(Santiago, Valparaíso, Concepción). La Patagonia interior, el Altiplano "
         "y la alta cordillera muestran vacíos de muestreo significativos.")

    if prov_data:
        df = pd.DataFrame(prov_data[:15])
        df = df[~df["provincia"].str.match(r"^\d+$", na=False)]
        fig = chart_hbar(df, "n", "provincia", "TOP PROVINCIAS · OBSERVACIONES HUMANAS")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Top 5 Regiones", "~45%", "concentran observaciones", delta_color="off")
    with c2:
        st.metric("Sin Provincia", "7.5M", "36% sin stateProvince", delta_color="off")
    with c3:
        st.metric("Sesgo Urbano", "ALTO", "Santiago >> Patagonia", delta_color="off")

# ═══════════════════════════════════════════════════════════════
# TAB 4: TEMPORAL
# ═══════════════════════════════════════════════════════════════
elif tab == "▸ TEMPORAL":
    st.markdown('<div class="cyber-section-title">◈ ¿CUÁNDO SE OBSERVA? · EVOLUCIÓN Y ESTACIONALIDAD</div>',
                 unsafe_allow_html=True)

    if year_data:
        df = pd.DataFrame(year_data)
        peak = df.loc[df["n"].idxmax()]
        recent = df[df["year"] >= 2020]["n"].sum()
        all_sum = df["n"].sum()
        kpi_row([
            (f"{int(peak['year'])}", "AÑO PICO", CYBER_CYAN, f"{peak['n']:,.0f} registros"),
            (numfmt(recent), "TOTAL 2020-2024", CYBER_AMBER, pctfmt(recent, all_sum)),
            (numfmt(all_sum), "TOTAL 1950+", CYBER_GREEN, "Observaciones Humanas"),
            ("x370", "CRECIMIENTO 1970-2023", CYBER_MAGENTA, "explosión post-eBird"),
        ])

    cyber_divider()

    if year_data:
        fig = chart_area(pd.DataFrame(year_data), "year", "n",
                         "OBSERVACIONES HUMANAS POR AÑO (1950-2025)")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    info("**Explosión post-2010.** eBird (2002) e iNaturalist (2008) revolucionaron "
         "la ciencia ciudadana. Entre 2020 y 2024 se registró el 38% de todas las "
         "observaciones humanas de la historia. La pandemia de COVID-19 impulsó el "
         "avistamiento de aves de traspatio.")

    if month_data:
        months = {1:"ENE",2:"FEB",3:"MAR",4:"ABR",5:"MAY",6:"JUN",
                  7:"JUL",8:"AGO",9:"SEP",10:"OCT",11:"NOV",12:"DIC"}
        df = pd.DataFrame(month_data)
        df["mes"] = df["month"].map(months)
        fig2 = px.bar(df, x="mes", y="n",
                       title="ESTACIONALIDAD · OBSERVACIONES POR MES",
                       color_discrete_sequence=[CYBER_CYAN])
        fig2.update_traces(hovertemplate="%{x}: <b>%{y:,.0f}</b><extra></extra>",
                            marker=dict(opacity=0.7))
        fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="cyber-section-title">◈ HITOS TEMPORALES</div>',
                 unsafe_allow_html=True)
    events = [
        ("2002", "Lanzamiento eBird", "Observación de aves digital"),
        ("2008", "Lanzamiento iNaturalist", "Plataforma para todos los taxones"),
        ("2010", ">800K registros/año", "Maduración de ciencia ciudadana"),
        ("2014", "Nodo GBIF Chile", "Integración nacional de datos"),
        ("2020", "COVID-19", "Auge de avistamientos desde casa"),
        ("2022", "Pico 1.8M", "Récord absoluto anual para Chile"),
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

# ═══════════════════════════════════════════════════════════════
# TAB 5: CALIDAD
# ═══════════════════════════════════════════════════════════════
elif tab == "▸ CALIDAD":
    st.markdown('<div class="cyber-section-title">◈ ¿QUÉ TAN CONFIABLES SON LOS DATOS?</div>',
                 unsafe_allow_html=True)

    if comp_data:
        tot = comp_data.get("total", 1)
        kpi_row([
            (pctfmt(comp_data.get("species_ok",0), tot), "CON ESPECIE", CYBER_GREEN,
             numfmt(comp_data.get("species_ok",0))),
            (pctfmt(comp_data.get("class_ok",0), tot), "CON CLASE", CYBER_AMBER,
             numfmt(comp_data.get("class_ok",0))),
            (pctfmt(comp_data.get("phylum_ok",0), tot), "CON PHYLUM", CYBER_CYAN,
             numfmt(comp_data.get("phylum_ok",0))),
            ("40.3%", "SIN CLASE", CYBER_RED, "8.3M sin clasificar"),
        ])

    cyber_divider()

    # Completeness chart
    if comp_data:
        tot = comp_data.get("total", 1)
        fields = [
            ("PHYLUM", comp_data.get("phylum_ok", 0)),
            ("CLASE", comp_data.get("class_ok", 0)),
            ("ORDEN", comp_data.get("order_ok", 0)),
            ("FAMILIA", comp_data.get("family_ok", 0)),
            ("GÉNERO", comp_data.get("genus_ok", 0)),
            ("ESPECIE", comp_data.get("species_ok", 0)),
            ("FECHA", comp_data.get("date_ok", 0)),
        ]
        df_c = pd.DataFrame(fields, columns=["CAMPO", "COMPLETO"])
        df_c["%"] = df_c["COMPLETO"] / tot * 100
        df_c["FALTANTE%"] = 100 - df_c["%"]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df_c["CAMPO"], x=df_c["%"], name="COMPLETO",
                              orientation="h", marker=dict(color=CYBER_GREEN, opacity=0.6)))
        fig.add_trace(go.Bar(y=df_c["CAMPO"], x=df_c["FALTANTE%"], name="FALTANTE",
                              orientation="h", marker=dict(color=CYBER_RED, opacity=0.4)))
        fig.update_layout(title="COMPLETITUD DE CAMPOS TAXONÓMICOS", barmode="stack",
                           bargap=0.3, xaxis_title="%", yaxis_title="",
                           showlegend=True, height=300)
        st.plotly_chart(fig, use_container_width=True)

    warn("**40.3% de los registros no tienen Clase asignada (8.3M).** "
         "Estos registros son virtualmente inutilizables para análisis taxonómicos "
         "sin procesamiento adicional.")

    if unc_data:
        unc_tot = unc_data.get("total", 1)
        sin = unc_data.get("sin_dato", 0)
        st.markdown('<div class="cyber-section-title">◈ INCERTIDUMBRE DE COORDENADAS</div>',
                     unsafe_allow_html=True)
        kpi_row([
            (pctfmt(sin, unc_tot), "SIN DATO DE PRECISIÓN", CYBER_RED, f"{numfmt(sin)} registros"),
            (f"{unc_data.get('mediana_m',0):,.0f}m", "MEDIANA (CUANDO HAY)", CYBER_AMBER),
            (f"{unc_data.get('promedio_m',0):,.0f}m", "PROMEDIO (CUANDO HAY)", CYBER_CYAN),
            ("7,945km", "INCERTIDUMBRE MÁX.", CYBER_MAGENTA, "FOSSIL_SPECIMEN"),
        ])

        cats = [("SIN DATO", sin, CYBER_RED), ("≤10m", unc_data.get("hasta_10m",0), CYBER_GREEN),
                ("10-100m", unc_data.get("de_10_100m",0), CYBER_GREEN),
                ("100m-1km", unc_data.get("de_100_1000m",0), CYBER_CYAN),
                ("1-10km", unc_data.get("de_1_10km",0), CYBER_AMBER),
                ("10-100km", unc_data.get("de_10_100km",0), CYBER_MAGENTA),
                (">100km", unc_data.get("mas_100km",0), CYBER_RED)]
        df_u = pd.DataFrame(cats, columns=["CATEGORÍA", "N", "COLOR"])
        df_u["%"] = df_u["N"] / unc_tot * 100
        fig_u = px.bar(df_u, x="N", y="CATEGORÍA", orientation="h", text="%",
                        title="DISTRIBUCIÓN DE INCERTIDUMBRE", color="COLOR",
                        color_discrete_map="identity")
        fig_u.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                             hovertemplate="%{y}: %{x:,.0f} (%{text:.1f}%)<extra></extra>")
        fig_u.update_layout(showlegend=False, yaxis=dict(autorange="reversed"),
                             xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_u, use_container_width=True)

    warn("**El 95% de los registros NO reportan coordinateUncertaintyInMeters.** "
         "Sin este campo, es imposible evaluar la precisión geoespacial. "
         "Para análisis serios, filtrá o asumí una incertidumbre por defecto.")

    st.markdown('<div class="cyber-section-title">◈ CHECKLIST DE CALIDAD</div>',
                 unsafe_allow_html=True)
    checks = [
        ("01", CYBER_GREEN, "Filtrar occurrenceStatus = PRESENT", "Excluye 1.17M registros ABSENT"),
        ("02", CYBER_GREEN, "Excluir FOSSIL_SPECIMEN", "7,379 fósiles con ~1,949km de incertidumbre"),
        ("03", CYBER_GREEN, "Revisar coordinateUncertaintyInMeters", "95% de registros sin este dato"),
        ("04", CYBER_AMBER, "Separar por basisOfRecord", "Comportamientos distintos según fuente"),
        ("05", CYBER_AMBER, "Verificar identificación taxonómica", "40.3% sin Clase asignada"),
    ]
    for num, color, check, detail in checks:
        st.markdown(f"""
        <div style="display:flex; gap:12px; margin:8px 0; font-family:'Rajdhani',sans-serif;">
            <span style="color:{color}; font-weight:bold; min-width:28px;">[{num}]</span>
            <span style="color:{CYBER_WHITE}; flex:1;">{check}</span>
            <span style="color:{CYBER_GRAY}; font-size:0.75rem;">{detail}</span>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 6: SESGOS
# ═══════════════════════════════════════════════════════════════
elif tab == "▸ SESGOS":
    st.markdown('<div class="cyber-section-title">◈ LO QUE EL DATO NO TE DICE · RADAR DE SESGOS</div>',
                 unsafe_allow_html=True)

    radar_dims = ["TAXONÓMICO\n(Aves >> Insectos)", "ESPACIAL\n(Urbano >> Rural)",
                  "TEMPORAL\n(Post-2010)", "ACCESIBILIDAD\n(Cerca de caminos)",
                  "DETECTABILIDAD\n(Grandes >> Pequeños)", "PLATAFORMA\n(Sesgo eBird/iNat)",
                  "CALIDAD\n(95% sin precisión)"]
    radar_vals = [9.0, 8.5, 7.0, 8.0, 7.5, 8.5, 9.0]
    fig_r = chart_radar(radar_dims, radar_vals, "RADAR DE SESGOS · 0=SIN SESGO / 10=SESGO EXTREMO")
    st.plotly_chart(fig_r, use_container_width=True)

    cyber_divider()

    if basis_dist:
        df_b = pd.DataFrame(basis_dist)
        colors_b = {"HUMAN_OBSERVATION": CYBER_CYAN, "MACHINE_OBSERVATION": CYBER_AMBER,
                     "PRESERVED_SPECIMEN": CYBER_MAGENTA, "FOSSIL_SPECIMEN": CYBER_RED}
        df_b["c"] = df_b["basis"].map(colors_b).fillna(CYBER_DIM)
        fig_b = chart_hbar(df_b, "n", "basis", "COMPARACIÓN DE FUENTES DE DATOS",
                           color_col="basis", colors=df_b["c"].tolist())
        st.plotly_chart(fig_b, use_container_width=True)

    coll, colr = st.columns(2)
    with coll:
        st.markdown(f"""
        <div class="cyber-radar-box" style="border-color:{CYBER_CYAN};">
            <div style="font-family:'Share Tech Mono',monospace; color:{CYBER_CYAN};
                        font-size:0.8rem; margin-bottom:6px;">■ OBSERVACIÓN HUMANA</div>
            <div style="color:{CYBER_GRAY}; font-size:0.75rem;">
                89.7% del dataset · Ciencia ciudadana<br>
                Dominado por eBird e iNaturalist<br>
                Sesgo hacia vertebrados grandes/diurnos<br>
                Concentración urbana y costera<br>
                Explosión de datos post-2010
            </div>
        </div>
        """, unsafe_allow_html=True)
    with colr:
        st.markdown(f"""
        <div class="cyber-radar-box" style="border-color:{CYBER_MAGENTA};">
            <div style="font-family:'Share Tech Mono',monospace; color:{CYBER_MAGENTA};
                        font-size:0.8rem; margin-bottom:6px;">■ ESPÉCIMEN DE MUSEO</div>
            <div style="color:{CYBER_GRAY}; font-size:0.75rem;">
                2.0% del dataset · Colecciones científicas<br>
                Mejor cobertura de invertebrados<br>
                Identificación taxonómica rigurosa<br>
                Distribución histórica más amplia<br>
                Menor sesgo espacial reciente
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="cyber-section-title">◈ GUÍA DE INTERPRETACIÓN</div>',
                 unsafe_allow_html=True)

    biases = [
        (CYBER_CYAN, "SESGO DE PLATAFORMA",
         "eBird representa >40% de las observaciones humanas. El dataset está dominado "
         "por observadores de aves, no por un muestreo representativo de la biodiversidad."),
        (CYBER_AMBER, "SESGO DE ACCESIBILIDAD",
         "Las observaciones se agrupan cerca de carreteras, ciudades y senderos turísticos. "
         "Áreas remotas (Patagonia interior, Altiplano, cordillera) están subrepresentadas."),
        (CYBER_MAGENTA, "SESGO DE DETECTABILIDAD",
         "Animales grandes, diurnos, coloridos o ruidosos están sobrerrepresentados. "
         "Invertebrados pequeños, especies nocturnas y crípticas están subrepresentados."),
        (CYBER_RED, "SESGO DE COMPLETITUD",
         "95% no reporta precisión de coordenadas. 40.3% no tiene Clase asignada. "
         "1.17M son registros ABSENT que se confunden con presencia. "
         "Sin filtrar, los mapas y estadísticas serán engañosos."),
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
            "UN DATO SIN CONTEXTO ES UN MAPA QUE MIENTE"
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="cyber-footer">
    ▸ GBIF.ORG · REGNUM ANIMALIA · CHILE (CL) · @CONMAPAS · {total:,.0f} REGISTROS ◂
</div>
""", unsafe_allow_html=True)
