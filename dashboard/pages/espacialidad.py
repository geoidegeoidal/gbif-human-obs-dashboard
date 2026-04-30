"""
Tab 3 — Espacialidad: ¿Dónde se observa?
Mapa de densidad, distribución por región, concentración geográfica.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.data.loader import get_data
from dashboard.data.queries import get_queries
from dashboard.components.kpi_cards import render_kpi_row, num_fmt, pct_fmt
from dashboard.components.graficos_plotly import bar_phylum
from dashboard.components.mapa_folium import map_from_coords
from dashboard.style import info_box
from dashboard.config import AMBER, CYAN, GREEN, RED, GRAY, GRAY_DIM


def show():
    st.header("Espacialidad")
    st.markdown(
        f'<p style="color:{GRAY};font-size:0.9rem;">'
        f'¿Dónde se concentran las observaciones humanas en Chile?'
        f'</p>',
        unsafe_allow_html=True,
    )

    # ---- Mapa principal ----
    st.subheader("Mapa de Densidad de Observaciones Humanas")

    layer_option = st.selectbox(
        "Capa del mapa",
        ["Heatmap (muestra 50K pts)", "Puntos individuales (muestra 5K pts)"],
    )

    if "Heatmap" in layer_option:
        df_sample, _ = get_data(
            "coords_sample",
            lambda: get_queries().sample_coords(50000, "HUMAN_OBSERVATION"),
        )
    else:
        df_sample, _ = get_data(
            "coords_sample_5k",
            lambda: get_queries().sample_coords(5000, "HUMAN_OBSERVATION"),
        )

    if isinstance(df_sample, pd.DataFrame) and len(df_sample) > 0:
        map_from_coords(df_sample)

    info_box(
        "<strong>Las observaciones humanas se concentran en zonas urbanas y costeras.</strong> "
        "Santiago, Valparaíso, Concepción y las capitales regionales concentran la mayor densidad. "
        "Zonas como la Patagonia, el altiplano y los Andes muestran vacíos de muestreo significativos."
    )

    # ---- Distribución por región ----
    st.subheader("Distribución por Región")

    prov_data, _ = get_data(
        "provincia_dist",
        lambda: get_queries().state_province_distribution("HUMAN_OBSERVATION")
        .to_dict(orient="records"),
    )
    if prov_data:
        df_prov = pd.DataFrame(prov_data).head(20)
        # Limpiar nombres: filtrar provincias numéricas
        df_prov = df_prov[~df_prov["provincia"].str.match(r"^\d+$", na=False)]
        fig = px.bar(
            df_prov,
            x="n", y="provincia", orientation="h",
            title="Top 20 Provincias con más Observaciones Humanas",
            color_discrete_sequence=[CYAN],
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        fig.update_traces(
            hovertemplate="%{y}: %{x:,.0f} registros<extra></extra>",
            marker=dict(opacity=0.7),
        )
        st.plotly_chart(fig, width="stretch")

    # ---- Concentración espacial ----
    st.subheader("Análisis de Concentración Espacial")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        prov_top = pd.DataFrame(prov_data).head(20) if prov_data else pd.DataFrame()
        if len(prov_top) > 0:
            total_human = prov_top["n"].sum() if "n" in prov_top.columns else 0
            top5 = prov_top.head(5)["n"].sum() if "n" in prov_top.columns else 0
            pct_top5 = top5 / total_human * 100 if total_human > 0 else 0
            st.metric(
                "Top 5 regiones concentran",
                f"{pct_top5:.1f}%",
                "de todas las observaciones humanas",
            )

    with col_b:
        st.metric(
            "Registros sin stateProvince",
            "7.54M",
            "36.3% no tiene provincia asignada",
        )

    info_box(
        "<strong>El 75.6% de los registros tienen stateProvince asignado.</strong> "
        "Sin embargo, los nombres de provincias son inconsistentes (ej: 'Bío-Bío' vs 'Región del Bíobío'), "
        "lo cual requiere limpieza para análisis geoespaciales precisos."
    )

    st.markdown(
        f'<p style="color:{GRAY_DIM};font-size:0.7rem;text-align:center;">'
        f'Fuente: GBIF.org · Reino Animalia · Chile (CL)'
        f'</p>',
        unsafe_allow_html=True,
    )

