"""
Tab 4 — Temporalidad: ¿Cuándo se observa?
Evolución anual, estacionalidad mensual, eventos de muestreo.
"""

import streamlit as st
import pandas as pd
from data.loader import get_data
from data.queries import get_queries
from components.kpi_cards import render_kpi_row, num_fmt, pct_fmt
from components.graficos_plotly import area_timeline, bar_month
from style import info_box
from config import AMBER, CYAN, GREEN, RED, GRAY, GRAY_DIM


def show():
    st.header("Temporalidad")
    st.markdown(
        f'<p style="color:{GRAY};font-size:0.9rem;">'
        f'¿Cuándo se realizan las observaciones humanas? Evolución y estacionalidad.'
        f'</p>',
        unsafe_allow_html=True,
    )

    # ---- Timeline ----
    st.subheader("Evolución Anual de Observaciones Humanas")

    year_data, _ = get_data(
        "year_human",
        lambda: get_queries().year_distribution("HUMAN_OBSERVATION", 1950)
        .to_dict(orient="records"),
    )
    if year_data:
        df_year = pd.DataFrame(year_data)

        # Destacar años recientes
        recent = df_year[df_year["year"] >= 2020]
        total_recent = recent["n"].sum() if len(recent) > 0 else 0
        total_all = df_year["n"].sum()
        peak_year_row = df_year.loc[df_year["n"].idxmax()]
        peak_year = int(peak_year_row["year"])
        peak_val = peak_year_row["n"]

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Pico máximo", f"{peak_val:,.0f}", f"Año {peak_year}")
        with col_b:
            st.metric("2020-2024", f"{total_recent:,.0f}",
                       f"{pct_fmt(total_recent, total_all)} del total")
        with col_c:
            st.metric("Total 1950+", f"{total_all:,.0f}", "Human Obs")

        fig = area_timeline(year_data, "Observaciones Humanas por Año (1950–2025)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, width="stretch")

    info_box(
        "<strong>Explosión post-2010.</strong> La ciencia ciudadana despegó con plataformas como "
        "eBird (2002) e iNaturalist (2008). Entre 2020 y 2024 se registró el ~38% de todas las "
        "observaciones humanas de la historia para Chile."
    )

    # ---- Estacionalidad ----
    st.subheader("Estacionalidad Mensual")

    month_data, _ = get_data(
        "month_dist",
        lambda: get_queries().month_distribution("HUMAN_OBSERVATION")
        .to_dict(orient="records"),
    )
    if month_data:
        fig2 = bar_month(month_data, "Observaciones Humanas por Mes (2000–2025)")
        st.plotly_chart(fig2, width="stretch")

    # ---- Análisis temporal detallado ----
    st.subheader("Hitos Temporales")

    events = [
        {"año": 2002, "evento": "Lanzamiento de eBird", "impacto": "Revolucionó el registro de aves a nivel global"},
        {"año": 2008, "evento": "Lanzamiento de iNaturalist", "impacto": "Ciencia ciudadana para todos los taxones"},
        {"año": 2010, "evento": "Primer pico > 800K registros/año", "impacto": "Maduración de plataformas ciudadanas"},
        {"año": 2014, "evento": "GBIF Chile formaliza nodo nacional", "impacto": "Mayor integración de datos chilenos"},
        {"año": 2020, "evento": "Pandemia COVID-19", "impacto": "Aumento de observaciones desde casa (backyard birding)"},
        {"año": 2022, "evento": "Récord: 1.8M+ registros en un año", "impacto": "Máximo histórico de observaciones humanas"},
    ]

    for ev in events:
        col_yr, col_desc = st.columns([0.15, 0.85])
        with col_yr:
            st.markdown(f"**{ev['año']}**")
        with col_desc:
            st.markdown(
                f"<span style='color:{CYAN};font-weight:bold;'>{ev['evento']}</span>"
                f"<br><span style='color:{GRAY};font-size:0.8rem;'>{ev['impacto']}</span>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<p style="color:{GRAY_DIM};font-size:0.7rem;text-align:center;">'
        f'Fuente: GBIF.org · Reino Animalia · Chile (CL)'
        f'</p>',
        unsafe_allow_html=True,
    )

