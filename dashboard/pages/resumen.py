"""
Tab 1 — Resumen ejecutivo.
KPIs principales + mapa overview + top phyla.
"""

import streamlit as st
import pandas as pd
from dashboard.data.loader import get_data, has_precomputed
from dashboard.data.queries import get_queries
from dashboard.components.kpi_cards import render_kpi_row, num_fmt, pct_fmt
from dashboard.components.graficos_plotly import (
    bar_basis, area_timeline,
)
from dashboard.components.mapa_folium import map_from_coords
from dashboard.style import info_box
from dashboard.config import AMBER, CYAN, MAGENTA, GREEN, RED, GRAY, GRAY_DIM


def show():
    st.header("Resumen Ejecutivo")
    st.markdown(
        f'<p style="color:{GRAY};font-size:0.9rem;">'
        f'Exploración de 20.8 millones de registros GBIF del reino Animalia en Chile.'
        f'</p>',
        unsafe_allow_html=True,
    )

    # ---- KPIs ----
    kpi_data, src = get_data("kpi", lambda: get_queries().kpi_totals().to_dict())
    total = kpi_data.get("total", 0)
    human = kpi_data.get("human_obs", 0)
    coords = kpi_data.get("with_coords", 0)
    absent = kpi_data.get("absent", 0)

    render_kpi_row([
        {"value": num_fmt(total), "label": "Total registros", "color": AMBER},
        {"value": num_fmt(human), "label": "Observaciones humanas", "color": CYAN,
         "subtitle": f"{pct_fmt(human, total)} del total"},
        {"value": num_fmt(coords), "label": "Con coordenadas", "color": GREEN,
         "subtitle": f"{pct_fmt(coords, total)} del total"},
        {"value": num_fmt(absent), "label": "Registros ABSENT", "color": RED,
         "subtitle": f"{pct_fmt(absent, total)} del total"},
    ])

    # ---- Info box ----
    info_box(
        "<strong>89.7% de todos los registros son HUMAN_OBSERVATION.</strong> "
        "Esto significa que los datos de GBIF para Chile están fuertemente dominados "
        "por ciencia ciudadana (eBird, iNaturalist), lo que introduce sesgos "
        "taxonómicos, espaciales y temporales importantes."
    )

    # ---- Dos columnas: mapa + distribucion ----
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Mapa de Observaciones Humanas")
        df_sample, src2 = get_data(
            "coords_sample",
            lambda: get_queries().sample_coords(50000, "HUMAN_OBSERVATION"),
        )
        if isinstance(df_sample, pd.DataFrame) and len(df_sample) > 0:
            st.caption("Muestra de 50,000 puntos de observación humana en Chile.")
            map_from_coords(df_sample)
        else:
            st.warning("No se encontraron coordenadas de muestra. Ejecutá precompute.py primero.")

    with col2:
        st.subheader("Fuente de los Datos")
        basis_data, src3 = get_data(
            "basis_dist",
            lambda: get_queries().basis_of_record_distribution()
            .rename(columns={"basisOfRecord": "basis"})
            .to_dict(orient="records"),
        )
        if basis_data:
            fig = bar_basis(basis_data)
            st.plotly_chart(fig, width="stretch")

        st.subheader("Evolución Temporal")
        year_data, src4 = get_data(
            "year_all",
            lambda: get_queries().year_distribution("HUMAN_OBSERVATION")
            .to_dict(orient="records"),
        )
        if year_data:
            fig2 = area_timeline(year_data, "Registros por Año (Human Obs)")
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, width="stretch")

    st.markdown(
        f'<p style="color:{GRAY_DIM};font-size:0.7rem;text-align:center;">'
        f'Fuente: GBIF.org · Reino Animalia · Chile (CL) · {src if src != "json" else "precomputado"}'
        f'</p>',
        unsafe_allow_html=True,
    )
