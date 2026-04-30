import numpy as np
import pandas as pd
import duckdb
import geopandas as gpd
from shapely.geometry import Polygon
import time

print("🚀 Generando grilla cuadrada de 25 km...")
t0 = time.perf_counter()

con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')

print("1. Extrayendo coordenadas (EPSG:3857, metros) desde GeoParquet...")
# The data in geoparquet/ is already in EPSG:3857 (meters)
df = con.sql("""
    SELECT ST_X(geometry) as x, ST_Y(geometry) as y
    FROM 'geoparquet/slide_02_raw_all.parquet'
""").fetchdf()

CELL_SIZE = 25000.0  # 25 km in meters

print("2. Calculando índices de la cuadrícula...")
# Simple math for square grids: floor divide coordinate by cell size
df['gx'] = np.floor(df['x'] / CELL_SIZE).astype(np.int32)
df['gy'] = np.floor(df['y'] / CELL_SIZE).astype(np.int32)

print("3. Agrupando y calculando densidad...")
counts = df.groupby(['gx', 'gy']).size().reset_index(name='n_puntos')
print(f"   Cuadrículas únicas con datos: {len(counts):,}")

print("4. Reconstruyendo geometrías de los cuadrados...")
# Esquina inferior izquierda del cuadrado
minx = counts['gx'] * CELL_SIZE
miny = counts['gy'] * CELL_SIZE

# Crear los polígonos cuadrados
polygons = []
for x, y in zip(minx, miny):
    # Cuadrado: (minx, miny) -> (maxx, miny) -> (maxx, maxy) -> (minx, maxy)
    poly = Polygon([
        (x, y),
        (x + CELL_SIZE, y),
        (x + CELL_SIZE, y + CELL_SIZE),
        (x, y + CELL_SIZE)
    ])
    polygons.append(poly)

counts['geometry'] = polygons
gdf = gpd.GeoDataFrame(counts, geometry='geometry', crs="EPSG:3857")

out_file = 'geoparquet/slide_02_raw_all_square_25km.parquet'
gdf.to_parquet(out_file)

print(f"\n✅ Terminado en {time.perf_counter()-t0:.1f}s")
print(f"   Guardado exitosamente en: {out_file}")
