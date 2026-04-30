import numpy as np
import duckdb
from scipy.ndimage import gaussian_filter
import rasterio
from rasterio.transform import from_origin
import time
import os

print("🚀 Generando Heatmap avanzado (GeoTIFF)...")
t0 = time.perf_counter()

con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')

print("1. Extrayendo coordenadas (EPSG:3857)...")
df = con.sql("""
    SELECT ST_X(geometry) as x, ST_Y(geometry) as y
    FROM 'geoparquet/slide_02_raw_all.parquet'
""").fetchdf()

N = len(df)
print(f"   Puntos totales (N): {N:,}")

xmin, xmax = df['x'].min(), df['x'].max()
ymin, ymax = df['y'].min(), df['y'].max()

A = (xmax - xmin) * (ymax - ymin)
print(f"   Área total del Bounding Box: {A / 10**6:,.0f} km²")

# Distancia media esperada al vecino más cercano en la distribución espacial
# Fórmula teórica: E[d] = 1 / (2 * sqrt(Densidad))
density = N / A
expected_distance = 1.0 / (2.0 * np.sqrt(density))

print(f"   Distancia media esperada geométrica: {expected_distance:.1f} metros")

# Tamaño de celda basado en la distancia media
CELL_SIZE = np.round(expected_distance)

# Prevent creating an outrageously large TIFF if points are too dense
ncols = int((xmax - xmin) / CELL_SIZE)
nrows = int((ymax - ymin) / CELL_SIZE)

max_pixels = 75_000_000  # Cap at ~75M pixels to avoid huge RAM spikes
if ncols * nrows > max_pixels:
    print(f"   ⚠️ La resolución nativa de {CELL_SIZE:.0f}m ({ncols}x{nrows}) es demasiado pesada.")
    scale = np.sqrt((ncols * nrows) / float(max_pixels))
    CELL_SIZE = np.round(CELL_SIZE * scale)
    ncols = int((xmax - xmin) / CELL_SIZE)
    nrows = int((ymax - ymin) / CELL_SIZE)

print(f"   Resolución final aplicada: {CELL_SIZE:.0f} m/pixel")
print(f"   Dimensiones de la matriz: {ncols:,} x {nrows:,} píxeles")

xmin = np.floor(xmin / CELL_SIZE) * CELL_SIZE
xmax = xmin + ncols * CELL_SIZE
ymin = np.floor(ymin / CELL_SIZE) * CELL_SIZE
ymax = ymin + nrows * CELL_SIZE

x_bins = np.linspace(xmin, xmax, ncols + 1)
y_bins = np.linspace(ymin, ymax, nrows + 1)

print("2. Calculando densidad y aplicando filtro Gaussiano...")
H, _, _ = np.histogram2d(df['x'], df['y'], bins=(x_bins, y_bins))
H = H.T
H = np.flipud(H) # La fila 0 debe representar el NORTE en rasters top-down

# Ancho de banda: suavizado de ~5-10 veces el tamaño de la celda
# para que el brillo se difumine y se junten los puntos vecinos
bandwidth = CELL_SIZE * 6.0 
sigma_pixels = bandwidth / CELL_SIZE

print(f"   Ancho de banda (Sigma): {bandwidth/1000:.1f} km ({sigma_pixels:.1f} píxeles)")

# Suavizado Gaussiano
heatmap = gaussian_filter(H, sigma=sigma_pixels)

# Limpiar valores ínfimos para que transparenten en el mapa (NoData)
heatmap[heatmap < 1e-5] = -9999.0

print("3. Exportando a GeoTIFF...")
out_file = 'geoparquet/slide_02_heatmap_distance.tif'

# Generar metadata de transformación
# El origen (top-left) es xmin y ymax, con pasos CELL_SIZE
transform = from_origin(xmin, ymax, CELL_SIZE, CELL_SIZE)

try:
    with rasterio.open(
        out_file,
        'w',
        driver='GTiff',
        height=heatmap.shape[0],
        width=heatmap.shape[1],
        count=1,
        dtype=heatmap.dtype,
        transform=transform,
        nodata=-9999.0,
        compress='lzw'
    ) as dst:
        dst.write(heatmap, 1)
except Exception as e:
    print(f"Error escribiendo GeoTIFF: {e}")

# Crear archivo .prj manual para saltarse el conflicto de PROJ de Windows
prj_file = out_file.replace('.tif', '.prj')
with open(prj_file, 'w') as f:
    f.write('PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","3857"]]')


print(f"\n✅ Terminado en {time.perf_counter()-t0:.1f}s")
print(f"   Guardado exitosamente: {out_file}")
