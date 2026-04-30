"""
Tab 5 — Calidad de datos: ¿Qué tan confiables son?
Incertidumbre, completitud taxonómica, ABSENT, checklist.
"""

import streamlit as st
from dashboard.data.loader import get_data
from dashboard.data.queries import get_queries
from dashboard.components.kpi_cards import render_kpi_row, num_fmt, pct_fmt
from dashboard.components.graficos_plotly import (
    bar_uncertainty, bar_completeness,
)
from dashboard.style import info_box, warning_box
from dashboard.config import AMBER, CYAN, MAGENTA, GREEN, RED, GRAY, GRAY_DIM


def show():
    st.header("Calidad de Datos")
    st.markdown(
        f'<p style="color:{GRAY};font-size:0.9rem;">'
        f'¿Qué tan confiables son los datos de observaciones humanas?'
        f'</p>',
        unsafe_allow_html=True,
    )

    # ---- Completitud taxonómica ----
    st.subheader("Completitud de Campos Taxonómicos")

    comp_data, _ = get_data(
        "completeness",
        lambda: get_queries().completeness_fields().to_dict(),
    )
    if comp_data:
        total = comp_data.get("total", 1)
        species_pct = comp_data.get("species_ok", 0) / total * 100
        class_pct = comp_data.get("class_ok", 0) / total * 100

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Con especie identificada", f"{species_pct:.1f}%",
                       f"{num_fmt(comp_data.get('species_ok', 0))}")
        with col_b:
            st.metric("Con class asignada", f"{class_pct:.1f}%",
                       f"{num_fmt(comp_data.get('class_ok', 0))}")
        with col_c:
            st.metric("Sin class", f"{100 - class_pct:.1f}%",
                       f"8.4M registros")

        fig = bar_completeness(comp_data)
        st.plotly_chart(fig, width="stretch")

    warning_box(
        "<strong>40.3% de los registros no tienen clase asignada (8.3M).</strong> "
        "Estos registros no son utilizables para análisis taxonómicos. "
        "Suelen ser observaciones de ciencia ciudadana donde el observador no identificó "
        "la especie a nivel taxonómico suficiente."
    )

    # ---- Incertidumbre ----
    st.subheader("Incertidumbre de Coordenadas")

    unc_data, _ = get_data(
        "uncertainty",
        lambda: get_queries().coordinate_uncertainty_distribution().to_dict(),
    )
    if unc_data:
        sin_dato = unc_data.get("sin_dato", 0)
        total_unc = unc_data.get("total", 1)
        mediana = unc_data.get("mediana_m")
        promedio = unc_data.get("promedio_m")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Sin dato de incertidumbre", f"{pct_fmt(sin_dato, total_unc)}",
                       "95% no reporta precisión")
        with col_b:
            st.metric("Mediana (cuando hay dato)", f"{mediana:,.0f} m" if mediana else "N/A")
        with col_c:
            st.metric("Promedio (cuando hay dato)", f"{promedio:,.0f} m" if promedio else "N/A")

        fig2 = bar_uncertainty(unc_data)
        st.plotly_chart(fig2, width="stretch")

    warning_box(
        "<strong>95% de los registros NO reportan coordinateUncertaintyInMeters.</strong> "
        "Esto significa que la mayoría de los puntos no tienen indicación de precisión. "
        "Sin este dato, no se puede evaluar la calidad geoespacial. "
        "Para análisis serios, se debe filtrar o asumir una incertidumbre por defecto."
    )

    # ---- Checklist de filtros ----
    st.subheader("Checklist: Antes de usar estos datos")

    checklist_items = [
        ("Filtrar occurrenceStatus = PRESENT", GREEN, "Excluye 1.17M registros ABSENT"),
        ("Excluir FOSSIL_SPECIMEN", GREEN, "7,379 fósiles con incertidumbre de ~1,949 km"),
        ("Revisar coordinateUncertaintyInMeters", GREEN, "95% de registros sin este dato"),
        ("Separar por basisOfRecord", AMBER, "Human vs Machine vs Museum: comportamientos distintos"),
        ("Verificar identificación taxonómica", AMBER, "40.3% sin class asignada"),
    ]

    for i, (text, color, detail) in enumerate(checklist_items):
        col_check, col_text = st.columns([0.05, 0.95])
        with col_check:
            st.markdown(f"### {i+1}.")
        with col_text:
            st.markdown(
                f"<span style='color:{color};font-weight:bold;'>✓ {text}</span>"
                f"<br><span style='color:{GRAY};font-size:0.8rem;'>{detail}</span>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<p style="color:{GRAY_DIM};font-size:0.7rem;text-align:center;">'
        f'Fuente: GBIF.org · Reino Animalia · Chile (CL)'
        f'</p>',
        unsafe_allow_html=True,
    )

