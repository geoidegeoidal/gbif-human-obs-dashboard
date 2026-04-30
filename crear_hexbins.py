import numpy as np
import pandas as pd
import duckdb
import geopandas as gpd
from shapely.geometry import Polygon
import time
import os

print("🚀 Generando grilla Hexbin de 25 km...")
t0 = time.perf_counter()

# Usamos DuckDB para extraer las coordenadas rápidamente del geoparquet
con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')

print("1. Extrayendo coordenadas desde GeoParquet...")
df = con.sql("""
    SELECT ST_X(geometry) as x, ST_Y(geometry) as y
    FROM 'geoparquet/slide_02_raw_all.parquet'
""").fetchdf()

# Queremos hexágonos orientados con punta hacia arriba (pointy-topped)
# Ancho (width) del hexágono = distancia de lado a lado = 25,000 metros (25 km)
# Para este tipo de hexágono, ancho = sqrt(3) * R
R = 25000.0 / np.sqrt(3)

print(f"   Radio del hexágono (R): {R:.1f} m")

# Convertimos coordenadas cartesianas (x,y) a coordenadas axiales hexagonales (q, r)
# (Algoritmo estándar de Red Blob Games)
print("2. Calculando coordenadas axiales (vectorizado para 20M pts)...")
q = (np.sqrt(3)/3 * df['x'] - 1/3 * df['y']) / R
r = (2.0/3.0 * df['y']) / R

# Convertimos a coordenadas cúbicas para redondear correctamente al hexágono más cercano
x_ax = q
z_ax = r
y_ax = -x_ax - z_ax

rx = np.round(x_ax)
ry = np.round(y_ax)
rz = np.round(z_ax)

x_diff = np.abs(rx - x_ax)
y_diff = np.abs(ry - y_ax)
z_diff = np.abs(rz - z_ax)

# Ajuste de redondeo para mantener x + y + z = 0
mask_x = (x_diff > y_diff) & (x_diff > z_diff)
mask_y = ~mask_x & (y_diff > z_diff)
mask_z = ~mask_x & ~mask_y

rx[mask_x] = -ry[mask_x] - rz[mask_x]
ry[mask_y] = -rx[mask_y] - rz[mask_y]
rz[mask_z] = -rx[mask_z] - ry[mask_z]

# Coordenadas finales del hexágono
df['q'] = rx.astype(np.int32)
df['r'] = rz.astype(np.int32)

print("3. Agrupando y calculando densidad...")
# Contamos cuántos puntos caen en cada hexágono (solo retenemos los > 0)
counts = df.groupby(['q', 'r']).size().reset_index(name='n_puntos')
print(f"   Hexágonos únicos con datos: {len(counts):,}")

print("4. Reconstruyendo geometrías de los hexágonos...")
# Coordenadas centrales de cada hexágono en el mapa
centers_x = R * np.sqrt(3) * (counts['q'] + counts['r'] / 2.0)
centers_y = R * 1.5 * counts['r']

# Esquinas del hexágono relativas al centro
angles_deg = np.array([30, 90, 150, 210, 270, 330])
angles_rad = np.deg2rad(angles_deg)
offset_x = R * np.cos(angles_rad)
offset_y = R * np.sin(angles_rad)

# Construir los polígonos
polygons = []
for cx, cy in zip(centers_x, centers_y):
    poly_x = cx + offset_x
    poly_y = cy + offset_y
    polygons.append(Polygon(zip(poly_x, poly_y)))

counts['geometry'] = polygons

# Convertir a GeoDataFrame
gdf = gpd.GeoDataFrame(counts, geometry='geometry', crs="EPSG:3857")

# Guardar en GeoParquet
out_file = 'geoparquet/slide_02_raw_all_hexbin_25km.parquet'
gdf.to_parquet(out_file)

print(f"\n✅ Terminado en {time.perf_counter()-t0:.1f}s")
print(f"   Guardado exitosamente en: {out_file}")
