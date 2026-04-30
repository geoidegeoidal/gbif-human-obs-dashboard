"""
Tab 6 — Sesgos y limitaciones: Lo que el dato NO te dice.
Radar de sesgos, comparaciones metodológicas, advertencias.
"""

import streamlit as st
from dashboard.data.loader import get_data
from dashboard.data.queries import get_queries
from dashboard.components.kpi_cards import render_kpi_row, num_fmt, pct_fmt
from dashboard.components.graficos_plotly import radar_sesgos, comparison_chart, bar_basis
from dashboard.style import info_box, warning_box
from dashboard.config import AMBER, CYAN, MAGENTA, GREEN, RED, GRAY, GRAY_DIM


def show():
    st.header("Sesgos y Limitaciones")
    st.markdown(
        f'<p style="color:{GRAY};font-size:0.9rem;">'
        f'Lo que los datos de observaciones humanas NO te están contando.'
        f'</p>',
        unsafe_allow_html=True,
    )

    # ---- Radar de sesgos ----
    st.subheader("Radar de Dimensiones de Sesgo")

    radar_data = {
        "Taxonómico (aves >> insectos)": 9.0,
        "Espacial (urbano >> rural)": 8.5,
        "Temporal (post-2010)": 7.0,
        "Accesibilidad (cerca de caminos)": 8.0,
        "Detección (grandes >> pequeños)": 7.5,
        "Plataforma (eBird/iNat bias)": 8.5,
        "Calidad (95% sin precisión)": 9.0,
    }
    fig = radar_sesgos(radar_data)
    st.plotly_chart(fig, width="stretch")

    info_box(
        "<strong>Cada dimensión se califica de 0 a 10</strong> donde 10 representa el sesgo más extremo. "
        "Un dataset sin sesgos tendría valores cercanos a 0. Este radar muestra que los datos de GBIF Chile "
        "tienen sesgos importantes en múltiples dimensiones simultáneamente."
    )

    # ---- Comparación metodológica ----
    st.subheader("Comparación: Fuentes de Datos")

    basis_data, _ = get_data(
        "basis_dist",
        lambda: get_queries().basis_of_record_distribution()
        .rename(columns={"basisOfRecord": "basis"})
        .to_dict(orient="records"),
    )
    if basis_data:
        fig2 = bar_basis(basis_data)
        st.plotly_chart(fig2, width="stretch")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(f"""
        **Human Observation (89.7%)**
        - Ciencia ciudadana: eBird, iNaturalist
        - Sesgo hacia vertebrados grandes/diurnos
        - Concentración urbana y costera
        - Explosión post-2010
        - Identificación taxonómica variable
        """)
    with col_b:
        st.markdown(f"""
        **Preserved Specimen (2.0%)**
        - Colecciones de museos
        - Mejor cobertura de invertebrados
        - Distribución histórica más amplia
        - Identificación taxonómica rigurosa
        - Menos sesgo espacial reciente
        """)

    # ---- Advertencias metodológicas ----
    st.subheader("Guía de Interpretación")
    st.markdown("---")

    advertencias = [
        (CYAN, "Sesgo de plataforma",
         "eBird representa >40% de las observaciones humanas. Esto significa que el dataset "
         "está dominado por observadores de aves, no por un muestreo representativo de la biodiversidad."),
        (AMBER, "Sesgo de accesibilidad",
         "Las observaciones se concentran cerca de carreteras, ciudades y senderos turísticos. "
         "Áreas remotas (Patagonia interior, altiplano, cordillera) están subrepresentadas."),
        (MAGENTA, "Sesgo de detectabilidad",
         "Animales grandes, diurnos, coloridos o ruidosos son sobrerrepresentados. "
         "Invertebrados pequeños, especies nocturnas y crípticas son subrepresentados."),
        (RED, "Sesgo de completitud",
         "95% no reporta precisión de coordenadas. 40.3% no tiene class asignada. "
         "1.17M son registros ABSENT que se confunden con presencia. "
         "Sin filtrar, los mapas y estadísticas serán engañosos."),
    ]

    for color, titulo, texto in advertencias:
        st.markdown(
            f"<div style='border-left:3px solid {color}; padding-left:1rem; margin:1rem 0;'>"
            f"<span style='color:{color};font-weight:bold;font-size:1rem;'>{titulo}</span>"
            f"<br><span style='color:{GRAY};font-size:0.85rem;'>{texto}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        f"<p style='color:{WHITE};font-size:1rem;text-align:center;font-weight:bold;'>"
        f'"Un dato sin contexto es un mapa que miente"</p>'
        f"<p style='color:{GRAY_DIM};font-size:0.7rem;text-align:center;'>"
        f'Fuente: GBIF.org · Reino Animalia · Chile (CL) · @conmapas'
        f'</p>',
        unsafe_allow_html=True,
    )

