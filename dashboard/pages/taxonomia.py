"""
Tab 2 — Taxonomía y cobertura: ¿Qué se observa?
Treemap de phyla, top especies, sesgo taxonómico.
"""

import streamlit as st
import pandas as pd
from dashboard.data.loader import get_data
from dashboard.data.queries import get_queries
from dashboard.components.kpi_cards import render_kpi_row, num_fmt, pct_fmt
from dashboard.components.graficos_plotly import (
    bar_phylum, bar_class, bar_species, comparison_chart,
)
from dashboard.style import info_box, warning_box
from dashboard.config import AMBER, CYAN, MAGENTA, GREEN, RED, GRAY, GRAY_DIM


def show():
    st.header("Taxonomía y Cobertura")
    st.markdown(
        f'<p style="color:{GRAY};font-size:0.9rem;">'
        f'¿Qué grupos de animales se están observando realmente?'
        f'</p>',
        unsafe_allow_html=True,
    )

    # ---- KPIs taxonómicos ----
    phylum_human, _ = get_data(
        "phylum_human",
        lambda: get_queries().phylum_distribution("HUMAN_OBSERVATION")
        .to_dict(orient="records"),
    )
    if phylum_human:
        total_human = sum(d["n"] for d in phylum_human)
        chordata_n = next((d["n"] for d in phylum_human if d["phylum"] == "Chordata"), 0)
        arthropoda_n = next((d["n"] for d in phylum_human if d["phylum"] == "Arthropoda"), 0)
        sin_dato_n = next((d["n"] for d in phylum_human if d["phylum"] == "Sin dato"), 0)
        render_kpi_row([
            {"value": num_fmt(chordata_n), "label": "Chordata", "color": CYAN,
             "subtitle": f"{pct_fmt(chordata_n, total_human)} human obs"},
            {"value": num_fmt(arthropoda_n), "label": "Arthropoda", "color": AMBER,
             "subtitle": f"{pct_fmt(arthropoda_n, total_human)} human obs"},
            {"value": num_fmt(sin_dato_n), "label": "Sin Class/Phylum", "color": RED,
             "subtitle": f"{pct_fmt(sin_dato_n, total_human)} sin clasificar"},
        ])

    # ---- Phylum chart ----
    col1, col2 = st.columns([1, 1])

    with col1:
        if phylum_human:
            fig = bar_phylum(phylum_human, "Phylum en Observaciones Humanas")
            st.plotly_chart(fig, width="stretch")

    with col2:
        class_human, _ = get_data(
            "class_human",
            lambda: get_queries().class_distribution("HUMAN_OBSERVATION")
            .to_dict(orient="records"),
        )
        if class_human:
            fig2 = bar_class(class_human, "Clases en Observaciones Humanas")
            st.plotly_chart(fig2, width="stretch")

    # ---- Top species ----
    st.subheader("Especies más Observadas")
    species_data, _ = get_data(
        "top_species",
        lambda: get_queries().top_species(20)
        .to_dict(orient="records"),
    )
    if species_data:
        fig3 = bar_species(species_data)
        st.plotly_chart(fig3, width="stretch")

    # ---- Sesgo Aves vs Insecta ----
    st.subheader("Sesgo Taxonómico: Vertebrados vs Invertebrados")
    aves_data, _ = get_data(
        "aves_insecta",
        lambda: get_queries().aves_vs_insecta_human_obs()
        .to_dict(orient="records"),
    )
    if aves_data:
        aves_n = next((d["n"] for d in aves_data if d["class"] == "Aves"), 0)
        insecta_n = next((d["n"] for d in aves_data if d["class"] == "Insecta"), 0)
        ratio = aves_n / insecta_n if insecta_n > 0 else 0

        col_a, col_b = st.columns([1, 1])
        with col_a:
            fig4 = comparison_chart(
                ["Aves", "Insecta"],
                [aves_n, insecta_n],
                None, "Human Obs", "",
                "Aves vs Insecta en Observaciones Humanas"
            )
            fig4.data = [fig4.data[0]]
            fig4.update_layout(showlegend=False)
            st.plotly_chart(fig4, width="stretch")
        with col_b:
            warning_box(
                f"<strong>Hay {ratio:.0f} aves por cada insecto registrado.</strong><br><br>"
                f"En observaciones humanas, las aves dominan por un factor de <strong>{ratio:.0f}:1</strong>. "
                f"Sin embargo, en especímenes de museo (PRESERVED_SPECIMEN), los insectos son mayoría "
                f"(249K insectos vs números mucho menores de aves).<br><br>"
                f"<em>Esto evidencia un sesgo fuerte de la ciencia ciudadana hacia vertebrados carismáticos.</em>"
            )

    st.markdown(
        f'<p style="color:{GRAY_DIM};font-size:0.7rem;text-align:center;">'
        f'Fuente: GBIF.org · Reino Animalia · Chile (CL)'
        f'</p>',
        unsafe_allow_html=True,
    )

