"""
Dashboard GBIF Human Observations
Entry point Streamlit.
"""

import streamlit as st
from dashboard.style import inject_css, footer
from dashboard.config import DASHBOARD_TITLE, DASHBOARD_SUBTITLE, AMBER, GRAY, GRAY_DIM
from dashboard.data.loader import has_precomputed

st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon=":globe_with_meridians:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---- Sidebar ----
with st.sidebar:
    st.markdown(
        f"<h2 style='color:{AMBER}; font-family: Impact, sans-serif;'>"
        f"GBIF Human Obs</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<p style='color:{GRAY}; font-size:0.8rem;'>{DASHBOARD_SUBTITLE}</p>", unsafe_allow_html=True)
    st.markdown("---")

    if has_precomputed():
        st.success("Usando datos precomputados")
    else:
        st.warning("Cargando datos en vivo desde CSV (lento)")

    st.markdown("### Navegación")
    tab = st.radio(
        "Seleccionar sección:",
        [
            "Resumen Ejecutivo",
            "Taxonomía y Cobertura",
            "Espacialidad",
            "Temporalidad",
            "Calidad de Datos",
            "Sesgos y Limitaciones",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"<p style='color:{GRAY_DIM}; font-size:0.7rem;'>"
        f"Datos: GBIF.org<br>Reino Animalia · Chile<br>@conmapas"
        f"</p>",
        unsafe_allow_html=True,
    )

# ---- Main content ----
st.markdown(
    f"<h1 style='font-family: Impact, sans-serif; color:{AMBER}; margin-bottom:0;'>"
    f"{DASHBOARD_TITLE}</h1>",
    unsafe_allow_html=True,
)

# Route to selected tab
if tab == "Resumen Ejecutivo":
    from dashboard.pages import resumen as pg
    pg.show()
elif tab == "Taxonomía y Cobertura":
    from dashboard.pages import taxonomia as pg
    pg.show()
elif tab == "Espacialidad":
    from dashboard.pages import espacialidad as pg
    pg.show()
elif tab == "Temporalidad":
    from dashboard.pages import temporalidad as pg
    pg.show()
elif tab == "Calidad de Datos":
    from dashboard.pages import calidad as pg
    pg.show()
elif tab == "Sesgos y Limitaciones":
    from dashboard.pages import sesgos as pg
    pg.show()

footer()
