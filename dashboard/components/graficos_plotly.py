"""
Componentes de gráficos Plotly con tema oscuro.
Genera figuras interactivas para el dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
from config import (
    BG, AMBER, CYAN, MAGENTA, GREEN, RED, WHITE, GRAY, GRAY_DIM,
    COLOR_PHYLUM, COLOR_BASIS, PLOTLY_COLOR_DISCRETE,
)

pio.templates["dark"] = go.layout.Template(
    layout=dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=GRAY, family="Segoe UI, sans-serif", size=12),
        title=dict(font=dict(color=WHITE, family="Impact, sans-serif")),
        xaxis=dict(gridcolor=GRAY_DIM, linecolor=GRAY_DIM, zerolinecolor=GRAY_DIM),
        yaxis=dict(gridcolor=GRAY_DIM, linecolor=GRAY_DIM, zerolinecolor=GRAY_DIM),
        legend=dict(font=dict(color=GRAY), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=20, t=50, b=20),
    )
)
pio.templates.default = "dark"


def bar_phylum(data, title="Distribución por Phylum"):
    """Bar chart horizontal de phyla."""
    df = pd.DataFrame(data)
    df = df[df["phylum"] != "Sin dato"].head(12)
    colors = [COLOR_PHYLUM.get(p, GRAY_DIM) for p in df["phylum"]]
    fig = px.bar(
        df, x="n", y="phylum", orientation="h",
        title=title, color="phylum",
        color_discrete_sequence=colors,
    )
    fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))
    fig.update_traces(hovertemplate="%{y}: %{x:,.0f} registros<extra></extra>")
    return fig


def bar_class(data, title="Top Clases", top_n=15):
    """Bar chart horizontal de clases."""
    df = pd.DataFrame(data)
    df = df[df["class"] != "Sin dato"].head(top_n)
    colors = [COLOR_PHYLUM.get(p, GRAY_DIM) for p in df["phylum"]]
    fig = px.bar(
        df, x="n", y="class", orientation="h",
        title=title, color="phylum",
        color_discrete_sequence=colors,
        hover_data=["phylum"],
    )
    fig.update_layout(showlegend=True, yaxis=dict(autorange="reversed"))
    fig.update_traces(hovertemplate="%{y}: %{x:,.0f}<br>Phylum: %{customdata[0]}<extra></extra>")
    return fig


def bar_species(data, title="Top Especies (Human Observations)"):
    """Bar chart horizontal de especies."""
    df = pd.DataFrame(data).head(20)
    colors = [COLOR_PHYLUM.get(c, GRAY_DIM) for c in df["class"]]
    fig = px.bar(
        df, x="n", y="species", orientation="h",
        title=title, color="class",
        color_discrete_sequence=colors,
    )
    fig.update_layout(showlegend=True, yaxis=dict(autorange="reversed"))
    fig.update_traces(hovertemplate="%{y}: %{x:,.0f}<extra></extra>")
    return fig


def bar_basis(data, title="Distribución por Basis of Record"):
    """Bar chart horizontal de basisOfRecord."""
    df = pd.DataFrame(data)
    colors = [COLOR_BASIS.get(b, GRAY_DIM) for b in df["basis"]]
    fig = px.bar(
        df, x="n", y="basis", orientation="h",
        title=title, color="basis",
        color_discrete_sequence=colors,
    )
    fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"),
                       xaxis_title="", yaxis_title="")
    fig.update_traces(hovertemplate="%{y}: %{x:,.0f}<extra></extra>")
    return fig


def area_timeline(data, title="Evolución Temporal"):
    """Área chart de evolución anual."""
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["n"],
        fill="tozeroy", mode="lines",
        line=dict(color=CYAN, width=2),
        fillcolor="rgba(34,211,238,0.15)",
        hovertemplate="Año %{x}: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Año", yaxis_title="Registros",
    )
    return fig


def bar_month(data, title="Estacionalidad de Observaciones"):
    """Bar chart de distribución mensual."""
    df = pd.DataFrame(data)
    months_map = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
    }
    df["mes"] = df["month"].map(months_map)
    fig = px.bar(
        df, x="mes", y="n",
        title=title, color_discrete_sequence=[CYAN],
    )
    fig.update_traces(
        hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
        marker=dict(opacity=0.7),
    )
    fig.update_layout(xaxis_title="", yaxis_title="Registros", showlegend=False)
    return fig


def bar_uncertainty(data, title="Incertidumbre de Coordenadas"):
    """Bar chart horizontal de incertidumbre."""
    total = data.get("total", 1)
    categories = [
        ("Sin dato", data.get("sin_dato", 0), RED),
        ("≤ 10m", data.get("hasta_10m", 0), GREEN),
        ("10-100m", data.get("de_10_100m", 0), GREEN),
        ("100m-1km", data.get("de_100_1000m", 0), CYAN),
        ("1-10km", data.get("de_1_10km", 0), AMBER),
        ("10-100km", data.get("de_10_100km", 0), MAGENTA),
        (">100km", data.get("mas_100km", 0), RED),
    ]
    df = pd.DataFrame(categories, columns=["Categoria", "Registros", "Color"])
    df["%"] = df["Registros"] / total * 100
    fig = px.bar(
        df, x="Registros", y="Categoria", orientation="h",
        title=title, color="Color", color_discrete_map="identity",
        text="%",
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate="%{y}: %{x:,.0f} (%{text:.1f}%)<extra></extra>",
    )
    fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"),
                       xaxis_title="", yaxis_title="")
    return fig


def bar_completeness(data, title="Completitud de Campos Taxonómicos"):
    """Bar chart de completitud."""
    total = data.get("total", 1)
    fields = [
        ("Phylum", data.get("phylum_ok", 0)),
        ("Class", data.get("class_ok", 0)),
        ("Order", data.get("order_ok", 0)),
        ("Family", data.get("family_ok", 0)),
        ("Genus", data.get("genus_ok", 0)),
        ("Species", data.get("species_ok", 0)),
        ("Fecha", data.get("date_ok", 0)),
    ]
    df = pd.DataFrame(fields, columns=["Campo", "Completos"])
    df["%"] = df["Completos"] / total * 100
    df["Ausentes%"] = 100 - df["%"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Campo"], x=df["%"], name="Completo",
        orientation="h", marker=dict(color=GREEN, opacity=0.6),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=df["Campo"], x=df["Ausentes%"], name="Ausente",
        orientation="h", marker=dict(color=RED, opacity=0.4),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=title, barmode="stack", bargap=0.2,
        xaxis_title="%", yaxis_title="",
        showlegend=True,
    )
    return fig


def radar_sesgos(data, title="Radar de Sesgos"):
    """Spider/radar chart de dimensiones de sesgo."""
    categories = list(data.keys())
    values = list(data.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories,
        fill="toself", name="Sesgo",
        fillcolor="rgba(34,211,238,0.2)",
        line=dict(color=CYAN, width=2),
        hovertemplate="%{theta}: %{r:.1f}/10<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(
                visible=True, range=[0, 10],
                gridcolor=GRAY_DIM, linecolor=GRAY_DIM,
                tickfont=dict(color=GRAY),
            ),
            angularaxis=dict(
                gridcolor=GRAY_DIM, linecolor=GRAY_DIM,
                tickfont=dict(color=WHITE, size=11),
            ),
        ),
        showlegend=False,
    )
    return fig


def comparison_chart(categories, values_a, values_b, label_a, label_b, title):
    """Gráfico de comparación side-by-side."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=categories, x=values_a, name=label_a,
        orientation="h",
        marker=dict(color=CYAN, opacity=0.7),
    ))
    fig.add_trace(go.Bar(
        y=categories, x=values_b, name=label_b,
        orientation="h",
        marker=dict(color=AMBER, opacity=0.7),
    ))
    fig.update_layout(
        title=title, barmode="group", bargap=0.2,
        xaxis_title="Registros", yaxis_title="",
        showlegend=True,
    )
    return fig
