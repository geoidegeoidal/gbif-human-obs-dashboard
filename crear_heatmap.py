import numpy as np
import duckdb
from scipy.ndimage import gaussian_filter
import time
import os

print("🚀 Generando Heatmap (Raster ESRI ASCII)...")
t0 = time.perf_counter()

con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')

print("1. Extrayendo coordenadas (EPSG:3857)...")
df = con.sql("""
    SELECT ST_X(geometry) as x, ST_Y(geometry) as y
    FROM 'geoparquet/slide_02_raw_all.parquet'
""").fetchdf()

print("2. Creando matriz 2D de densidad base...")
# Parámetros del Heatmap
CELL_SIZE = 2000.0  # Resolución del pixel: 2 km
SIGMA_KM = 20.0     # Ancho de banda (radio de influencia) de 20 km
SIGMA_PIXELS = (SIGMA_KM * 1000) / CELL_SIZE

print(f"   Resolución: {CELL_SIZE/1000:.1f} km/pixel | Ancho de banda (Sigma): {SIGMA_KM} km")

# Límites (Bounding box)
xmin, xmax = df['x'].min(), df['x'].max()
ymin, ymax = df['y'].min(), df['y'].max()

# Ajustar límites exactos a la cuadrícula
xmin = np.floor(xmin / CELL_SIZE) * CELL_SIZE
xmax = np.ceil(xmax / CELL_SIZE) * CELL_SIZE
ymin = np.floor(ymin / CELL_SIZE) * CELL_SIZE
ymax = np.ceil(ymax / CELL_SIZE) * CELL_SIZE

ncols = int((xmax - xmin) / CELL_SIZE)
nrows = int((ymax - ymin) / CELL_SIZE)

print(f"   Dimensiones de la imagen: {ncols} x {nrows} píxeles")

x_bins = np.linspace(xmin, xmax, ncols + 1)
y_bins = np.linspace(ymin, ymax, nrows + 1)

# Histograma 2D
H, _, _ = np.histogram2d(df['x'], df['y'], bins=(x_bins, y_bins))

# Trasponer para tener (y, x) -> (filas, columnas)
H = H.T
# Invertir eje Y para que la fila 0 sea el NORTE (requerido por formato ESRI)
H = np.flipud(H)

print("3. Aplicando filtro Gaussiano (Heatmap)...")
heatmap = gaussian_filter(H, sigma=SIGMA_PIXELS)

# (Opcional) eliminar áreas con densidad virtualmente cero para que queden transparentes/sin datos
heatmap[heatmap < 0.001] = -9999

print("4. Guardando archivo raster (.asc)...")
out_file = 'geoparquet/slide_02_heatmap_20km.asc'

header = f"ncols        {ncols}\n"
header += f"nrows        {nrows}\n"
header += f"xllcorner    {xmin}\n"
header += f"yllcorner    {ymin}\n"
header += f"cellsize     {CELL_SIZE}\n"
header += f"NODATA_value -9999\n"

with open(out_file, 'w') as f:
    f.write(header)
    np.savetxt(f, heatmap, fmt='%.4f')

print(f"\n✅ Terminado en {time.perf_counter()-t0:.1f}s")
print(f"   Guardado exitosamente: {out_file}")
print("   En QGIS: Arrástralo, dale doble clic -> Symbology -> Singleband pseudocolor")
