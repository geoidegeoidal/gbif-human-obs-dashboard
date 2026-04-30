"""
Configuración global del dashboard GBIF Human Observations.
Paleta de colores, constantes, paths y metadata.
"""

import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "0022205-260226173443078.csv")
PQ_PATH = os.path.join(BASE_DIR, "map_data.parquet")
GEOPQ_DIR = os.path.join(BASE_DIR, "geoparquet")
EDA_PATH = os.path.join(BASE_DIR, "eda_results.json")
METH_PATH = os.path.join(BASE_DIR, "eda_methodological.json")
PRECOMPUTE_DIR = os.path.join(BASE_DIR, "dashboard", "data", "precomputed")
os.makedirs(PRECOMPUTE_DIR, exist_ok=True)

# --- Colors (consistentes con el carrusel) ---
BG = "#0d1117"
AMBER = "#fbbf24"
CYAN = "#22d3ee"
MAGENTA = "#e879f9"
GREEN = "#4ade80"
RED = "#f87171"
WHITE = "#f1f5f9"
GRAY = "#94a3b8"
GRAY_DIM = "#475569"

# --- Colores por categoría ---
COLOR_PHYLUM = {
    "Chordata": CYAN,
    "Arthropoda": AMBER,
    "Mollusca": MAGENTA,
    "Annelida": GREEN,
    "Echinodermata": "#f97316",
    "Cnidaria": "#a78bfa",
    "Porifera": "#fb923c",
    "Platyhelminthes": "#818cf8",
    "Bryozoa": "#c084fc",
    "Nematoda": "#fbbf24",
    "Rotifera": "#34d399",
    "Tardigrada": "#f472b6",
    "Brachiopoda": "#a3e635",
    "Otros": GRAY_DIM,
}

COLOR_BASIS = {
    "HUMAN_OBSERVATION": CYAN,
    "MACHINE_OBSERVATION": AMBER,
    "PRESERVED_SPECIMEN": MAGENTA,
    "OBSERVATION": GREEN,
    "MATERIAL_SAMPLE": "#f97316",
    "LIVING_SPECIMEN": "#a78bfa",
    "FOSSIL_SPECIMEN": RED,
    "Otros": GRAY_DIM,
}

# --- Plotly template oscuro ---
PLOTLY_DARK_TEMPLATE = {
    "layout": {
        "paper_bgcolor": BG,
        "plot_bgcolor": BG,
        "font": {"color": GRAY, "family": "Segoe UI, sans-serif"},
        "title": {"font": {"color": WHITE}},
        "xaxis": {
            "gridcolor": GRAY_DIM,
            "linecolor": GRAY_DIM,
            "zerolinecolor": GRAY_DIM,
        },
        "yaxis": {
            "gridcolor": GRAY_DIM,
            "linecolor": GRAY_DIM,
            "zerolinecolor": GRAY_DIM,
        },
        "legend": {"font": {"color": GRAY}},
    }
}

# --- Plotly color scales ---
PLOTLY_COLOR_DISCRETE = [CYAN, AMBER, MAGENTA, GREEN, RED,
                          "#f97316", "#a78bfa", "#fb923c",
                          "#818cf8", "#c084fc", "#34d399",
                          "#f472b6", "#a3e635"]

# --- Metadata ---
TOTAL_ROWS = 20_801_113
TOTAL_HUMAN_OBS = 18_662_018
TOTAL_WITH_COORDS = 20_636_696
TOTAL_ABSENT = 1_170_113
TOTAL_FOSSIL = 7_379
PCT_CHORDATA = 82.6
PCT_ARTHROPODA = 14.8
PCT_HUMAN_OBS = 89.7

# --- Títulos y descripciones ---
DASHBOARD_TITLE = "GBIF Human Observations | Dashboard"
DASHBOARD_SUBTITLE = "Exploración de 20.8 millones de observaciones de animales en Chile"
SOURCE_TEXT = "Fuente: GBIF.org · Reino Animalia · Chile (CL)"
CREDITS = "Dashboard por @conmapas"
