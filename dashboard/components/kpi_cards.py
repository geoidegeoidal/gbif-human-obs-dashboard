"""
Componentes reutilizables: tarjetas KPI.
"""

import streamlit as st
from dashboard.config import AMBER, CYAN, MAGENTA, GREEN, RED, WHITE, GRAY, GRAY_DIM


def render_kpi_row(kpis):
    """
    Renderiza una fila de tarjetas KPI.
    kpis: lista de dicts con keys: value, label, color (opcional), subtitle (opcional)
    """
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            value = kpi.get("value", "")
            label = kpi.get("label", "")
            color = kpi.get("color", AMBER)
            subtitle = kpi.get("subtitle", "")
            sub_html = f'<span style="color:{GRAY_DIM}; font-size:0.7rem;">{subtitle}</span><br>' if subtitle else ""
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #111827, #0f172a);
                border: 1px solid {GRAY_DIM};
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                margin: 0.2rem 0;
            ">
                <div style="font-size:1.8rem; font-weight:900; color:{color}; line-height:1.2;">{value}</div>
                <div style="font-size:0.75rem; color:{GRAY}; text-transform:uppercase; letter-spacing:0.05em;">{label}</div>
                {sub_html}
            </div>
            """, unsafe_allow_html=True)


def num_fmt(n):
    """Formatea números grandes: 18.7M, 1.2M, 425K."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(int(n))


def pct_fmt(n, total):
    """Formatea porcentaje."""
    if total == 0:
        return "0%"
    return f"{n / total * 100:.1f}%"
