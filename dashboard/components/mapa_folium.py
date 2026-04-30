"""
Componentes de mapas usando Folium + Streamlit.
Genera mapas interactivos con datos del dashboard.
"""

import folium
from folium import plugins
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd
import numpy as np
from dashboard.config import BG, CYAN, AMBER, RED, GRAY


def create_base_map(center_lat=-35, center_lon=-71, zoom=5):
    """Crea un mapa base de Folium centrado en Chile."""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles=None,
        control_scale=True,
    )
    # Tile oscuro (CartoDB Dark Matter)
    folium.TileLayer(
        tiles="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
        attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="Dark",
        control=True,
    ).add_to(m)
    return m


def add_heatmap_layer(m, df, name="Densidad", radius=12, blur=10):
    """Agrega capa HeatMap a partir de un DataFrame con columnas lat, lon."""
    from folium.plugins import HeatMap
    coords = df[["lat", "lon"]].values.tolist()
    HeatMap(
        coords,
        name=name,
        radius=radius,
        blur=blur,
        gradient={0.2: "blue", 0.4: "cyan", 0.6: "lime", 0.8: "yellow", 1.0: "red"},
        max_zoom=10,
    ).add_to(m)
    return m


def add_marker_cluster(m, df, name="Observaciones", max_points=3000):
    """Agrega capa de puntos con cluster."""
    from folium.plugins import MarkerCluster
    cluster = MarkerCluster(name=name).add_to(m)
    sample = df.sample(min(len(df), max_points))
    for _, row in sample.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=2,
            color=CYAN,
            fill=True,
            fill_opacity=0.3,
            stroke=False,
        ).add_to(cluster)
    return m


def create_hexbin_map(df, hexbin_size=0.5, name="Hexbin"):
    """Crea mapa con hexbins usando datos con lat/lon desde precomputado."""
    m = create_base_map()
    if len(df) == 0:
        return m

    # Si los datos vienen del precomputado (q, r, n_puntos), renderizar hexágonos
    if "geometry" not in df.columns:
        # Datos de puntos raw - usar heatmap
        return add_heatmap_layer(m, df)

    return m


def human_obs_map(df_sample):
    """Mapa principal de observaciones humanas."""
    m = create_base_map()
    if len(df_sample) == 0:
        return m

    add_heatmap_layer(m, df_sample, name="Observaciones Humanas")
    folium.LayerControl().add_to(m)
    return m


def render_map(m, height=500, width="100%"):
    """Renderiza un mapa Folium en Streamlit."""
    st_folium(m, height=height, width=width, returned_objects=[])


def map_from_coords(df, title="Mapa de Observaciones Humanas"):
    """Toma un DataFrame con lat, lon y devuelve mapa centrado en Chile."""
    if len(df) == 0:
        st.warning("Sin datos de coordenadas disponibles.")
        return
    m = human_obs_map(df)
    render_map(m)
