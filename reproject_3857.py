"""
Re-export GeoParquet datasets in EPSG:3857 (Pseudo-Mercator).
Reads from existing geoparquet/ files (EPSG:4326) and reprojects.
"""
import geopandas as gpd
import os, time

IN_DIR = 'geoparquet'
files = [
    'slide_02_raw_all.parquet',
    'slide_09_phylum.parquet',
    'slide_10_class.parquet',
    'slide_11_basis.parquet',
]

for f in files:
    t0 = time.perf_counter()
    path = os.path.join(IN_DIR, f)
    print(f"Reprojecting {f}...", end=' ', flush=True)
    gdf = gpd.read_parquet(path)
    gdf = gdf.to_crs(epsg=3857)
    gdf.to_parquet(path)
    dt = time.perf_counter() - t0
    size = os.path.getsize(path) / 1024 / 1024
    print(f"OK ({len(gdf):,.0f} rows, {size:.0f} MB, {dt:.1f}s)")

print("\n✅ All GeoParquet files reprojected to EPSG:3857 (Pseudo-Mercator)")
